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
            else:
                model_name = getattr(serializer_meta, "model_name", None)
        for field, errors in super().errors.items():
            prefix = ""
            if isinstance(errors, (dict,)) and len(errors) > 0:
                errors = errors[next(iter(errors))]
                prefix = "item_"
            for error in errors:
                if not isinstance(error, (dict,)):
                    error_out = {
                        "resource": model_name,
                        "field": field,
                        "code": prefix + ("nulled" if error.code == "null" else error.code),
                    }
                    output.append(error_out)
                else:
                    for sub_field, sub_errors in error.items():
                        sub_error = next(iter(sub_errors))
                        error_out = {
                            "resource": model_name,
                            "field": ".".join([field, sub_field]),
                            "code": ("nulled" if sub_error.code == "null" else sub_error.code)
                        }
                        output.append(error_out)
        return output
