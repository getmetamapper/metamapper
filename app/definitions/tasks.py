# -*- coding: utf-8 -*-
from app.definitions.models import Datastore
from metamapper.celery import app


__all__ = ['hard_delete_datastore']


@app.task(bind=True)
def hard_delete_datastore(self, datastore_id, *args, **kwargs):
    """Background task to permanently delete a datastore. This is primarly done
    to avoid memory issues and improve the UI experience.
    """
    Datastore.all_objects.filter(id=datastore_id).hard_delete()
