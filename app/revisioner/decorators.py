# -*- coding: utf-8 -*-


def track_revised_properties(cls):
    """Tracked properties
    """
    cls.on_create = []
    cls.on_modify = []
    for method in dir(cls):
        fcn = getattr(cls, method)
        if hasattr(fcn, "on_create"):
            cls.on_create.append(fcn)
        if hasattr(fcn, "on_modify"):
            cls.on_modify.append(fcn)
    return cls


def on_create_property(fcn):
    """Mark a property as a CREATED action.
    """
    fcn.on_create = True
    return fcn


def on_modify_property(fcn):
    """Mark a property as a MODIFIED action.
    """
    fcn.on_modify = True
    return fcn
