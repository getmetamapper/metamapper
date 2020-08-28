# -*- coding: utf-8 -*-
from app.authentication.models import Workspace
from metamapper.celery import app


__all__ = ['hard_delete_workspace']


@app.task(bind=True)
def hard_delete_workspace(self, workspace_id, *args, **kwargs):
    """Background task to permanently delete a workspace. This is primarly done
    to avoid memory issues and improve the UI experience.
    """
    Workspace.all_objects.filter(id=workspace_id).hard_delete()
