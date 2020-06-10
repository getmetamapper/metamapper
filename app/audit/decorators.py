# -*- coding: utf-8 -*-
from functools import wraps
from app.audit import tasks


def capture_activity(verb, hydrater, capture_changes=False, logger=None):
    """Decorator to capture audit activities.
    """
    def the_decorator(func):
        @wraps(func)
        def func_wrapper(self, *args, **kwargs):
            """This has to be attached to a serializer.
            """
            request = self.context.get('request')
            instance = func(self, *args, **kwargs)

            if instance:
                audit_kwargs = {
                    'verb': verb,
                    'old_values': {},
                    'new_values': {},
                }
                audit_kwargs.update(hydrater(instance))

                if capture_changes:
                    old_values = instance.get_old_values()
                    old_fields = list(old_values.keys())

                    update_kwargs = {
                        'old_values': old_values,
                        'new_values': instance.get_new_values(old_fields)
                    }
                    audit_kwargs.update(update_kwargs)

                    # We need to save when we want to record changes.
                    instance.save()

                if request:
                    tasks.audit.delay(
                        request.user.pk,
                        request.workspace.pk,
                        **audit_kwargs,
                    )
            return instance
        return func_wrapper
    return the_decorator
