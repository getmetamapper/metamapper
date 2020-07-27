# -*- coding: utf-8 -*-
import requests

from django.conf import settings
from rest_framework import status
from requests.exceptions import ConnectionError

from metamapper import get_version, is_docker
from metamapper.celery import app

from utils import logging

from app.authentication.models import Workspace
from app.authorization.models import Group
from app.comments.models import Comment
from app.customfields.models import CustomField


@app.task(bind=True)
@logging.task_logger(__name__)
def send_beacon(self):
    """If enabled, send a Beacon to a remote server operated by the Metamapper team.
    """
    if not settings.METAMAPPER_BEACON_ACTIVATED:
        self.log.info("beacon.skipped.disabled")
        return

    if settings.DEBUG:
        self.log.info("beacon.skipped.debug")
        return

    for workspace in Workspace.objects.filter(beacon_consent=True):
        customproperties = 0
        for model_name in CustomField.SUPPORTED_MODELS:
            count = CustomField.get_content_type_from_name(model_name).model_class().objects.filter(
                workspace_id=workspace.id,
            ).exclude(
                custom_properties={},
            ).count()
            customproperties += count

        payload = {
            "docker": is_docker(),
            "version": get_version(),
            "workspace_id": str(workspace.id),
            "usage": {
                "team": workspace.team_members.count(),
                "datastores": workspace.datastores.count(),
                "groups": Group.objects.filter(workspace_id=workspace.id).count(),
                "comments": Comment.objects.filter(workspace_id=workspace.id).count(),
                "customfields": CustomField.objects.filter(workspace_id=workspace.id).count(),
                "customproperties": customproperties,
            },
        }

        try:
            response = requests.post(
                url="https://beacon.metamapper.cloud/usage",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
        except ConnectionError:
            response = None

        self.log.info(payload)

        if not response or response.status_code >= status.HTTP_400_BAD_REQUEST:
            self.log.warning(f"(wksp: {workspace.id}) beacon.failed")
        else:
            self.log.info(f"(wksp: {workspace.id}) beacon.sent")
