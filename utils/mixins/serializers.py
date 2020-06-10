# -*- coding: utf-8 -*-


class MetamapperSerializer(object):
    """Custom mixin for all Metamapper serializer classes.
    """
    @property
    def errors(self):
        output = []
        model_name = None
        serializer_meta = getattr(self, "Meta", None)
        if serializer_meta:
            model_class = getattr(serializer_meta, "model", None)
            if model_class:
                model_name = str(model_class.__name__)
        for field, errors in super().errors.items():
            prefix = ""
            if isinstance(errors, (dict,)) and len(errors) > 0:
                errors = errors[next(iter(errors))]
                prefix = "item_"
            output += [
                {
                    "resource": model_name,
                    "field": field,
                    "code": prefix + ("nulled" if error.code == "null" else error.code),
                }
                for error in errors
            ]
        return output
