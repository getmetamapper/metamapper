# -*- coding: utf-8 -*-
from metamapper.celery import app

from datetime import timedelta
from django.utils.timezone import now

from app.audit.models import Activity


@app.task(bind=True)
def audit(self,
          actor_id,
          workspace_id,
          verb,
          old_values,
          new_values,
          extras=None,
          target_object_id=None,
          target_content_type_id=None,
          action_object_object_id=None,
          action_object_content_type_id=None):
    """Task to commit an audit activity to a database.
    """
    activity_kwargs = {
        'actor_id': actor_id,
        'workspace_id': workspace_id,
        'verb': verb,
        'target_object_id': target_object_id,
        'target_content_type_id': target_content_type_id,
        'action_object_object_id': action_object_object_id,
        'action_object_content_type_id': action_object_content_type_id,
    }

    defaults = {
        'extras': extras or {},
        'timestamp': now(),
        'old_values': old_values,
        'new_values': new_values,
    }

    datefrom = now() - timedelta(minutes=15)
    queryset = (
        Activity.objects
                .filter(**activity_kwargs)
                .filter(timestamp__gte=datefrom)
    )

    for field in old_values.keys():
        queryset = queryset.filter(old_values__has_key=field)

    activity = queryset.first()

    if activity:
        activity.update_attributes(**defaults)
    else:
        activity_kwargs.update(defaults)
        activity = Activity.objects.create(**activity_kwargs)

    return activity.pk
