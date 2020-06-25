# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.utils import OperationalError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.healthchecks.models import Heartbeat, HEALTHY, UNHEALTHY, NOT_CONFIGURED
from app.healthchecks.tasks import add

from metamapper.celery import app


def do_metastore_check(*args, **kwargs):
    """Perform a status check on the database.
    """
    try:
        record = ContentType.objects.first()
    except OperationalError:
        record = None
    return {"status": HEALTHY if record else UNHEALTHY}


def do_scheduler_check(*args, **kwargs):
    """Perform a status check on the Celery beat scheduler.
    """
    heartbeat = Heartbeat.objects.first()

    if not heartbeat:
        return {
            "status": UNHEALTHY,
            "latest_scheduler_heartbeat": None,
        }

    return {
        "status": heartbeat.status,
        "latest_scheduler_heartbeat": heartbeat.ts,
    }


def do_worker_check(timeout):
    """Perform a status check on the Celery worker.
    """
    if not app.conf.result_backend:
        return {"status": NOT_CONFIGURED}

    try:
        result = add.apply_async(
            args=[4, 4],
            expires=timeout,
        )
        is_healthy = result.get(timeout=timeout) == 8
    except Exception as e:
        is_healthy = False

    return {"status": HEALTHY if is_healthy else UNHEALTHY}


@api_view(['GET'])
def healthcheck(request):
    """Check to see if certain Metamapper services are healthy.

    Example Response:

    {
        "metastore": {
            "status": "healthly"
        },
        "scheduler": {
            "status": "healthy",
            "latest_scheduler_heartbeat": "2020-07-21 05:23:19+00:00"
        },
        "worker": {
            "status": "healthly"
        }
    }
    """
    response_kwargs = {
        "metastore": do_metastore_check(),
        "scheduler": do_scheduler_check(),
        "worker": do_worker_check(timeout=3),
    }

    return Response(response_kwargs, status=status.HTTP_200_OK)
