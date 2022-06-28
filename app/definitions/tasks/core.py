# -*- coding: utf-8 -*-
from app.definitions.models import Datastore, Schema, Table, Column
from metamapper.celery import app


__all__ = ['hard_delete_datastore']


@app.task(bind=True)
def hard_delete_datastore(self, datastore_id, *args, **kwargs):
    """Background task to permanently delete a datastore. This is primarly done
    to avoid memory issues and improve the UI experience.
    """
    Column.all_objects.filter(table__schema__datastore_id=datastore_id).hard_delete()
    Table.all_objects.filter(schema__datastore_id=datastore_id).hard_delete()
    Schema.all_objects.filter(datastore_id=datastore_id).hard_delete()
    Datastore.all_objects.filter(id=datastore_id).hard_delete()
