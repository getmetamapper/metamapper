# -*- coding: utf-8 -*-
from utils import logging

from metamapper.celery import app

from app.inspector import service as inspector
from app.definitions.models import Datastore


__all__ = ['check_version']


@app.task(bind=True)
@logging.task_logger(__name__)
def check_version(self, datastore_id):
    """Check if the version of the datastore needs to be updated.
    """
    datastore = Datastore.objects.get(id=datastore_id)
    OperError = inspector.get_engine(datastore).operational_error

    try:
        dbversion = inspector.version(datastore)
    except OperError:
        return

    if dbversion != datastore.version:
        datastore.version = dbversion
        datastore.save()
