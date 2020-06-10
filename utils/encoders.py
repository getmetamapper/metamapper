# -*- coding: utf-8 -*-
import json

from django.db import models


class DjangoPartialModelJsonEncoder(json.JSONEncoder):
    """Encode JSON with a Django model inside. This is primarily used to
    in lieu of pickling an object. We can re-hydrate it based on the
    stored "pk" field if needed.
    """
    def default(self, obj):
        if isinstance(obj, models.Model):
            return {'pk': str(obj.pk), 'type': obj.__class__.__name__}
        return json.JSONEncoder.default(self, obj)
