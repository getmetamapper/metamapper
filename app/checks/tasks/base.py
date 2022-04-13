# -*- coding: utf-8 -*-
import functools

from rest_framework.serializers import Field


class ExpectationFailed(Exception):
    """Generic error for when an expectation does not pass.
    """


class InputFieldsMixin(object):
    """docstring for PassValue
    """
    class Input:
        """Metaclass for required inputs to class.
        """

    def __init__(self, **input_data):
        self.input_data = input_data

    @classmethod
    def get_fields(cls):
        d = {}
        for k, v in cls.Input.__dict__.items():
            if isinstance(v, Field):
                d[k] = v
        return [(k,v) for k, v in d.items()]

    @property
    @functools.lru_cache(maxsize=None)
    def fields(self):
        return self.__class__.get_fields()

    @property
    def field_names(self):
        return [f[0] for f in self.fields]

    @property
    @functools.lru_cache(maxsize=None)
    def inputs(self):
        d = {}
        for f in self.field_names:
            d[f] = self.input_data.get(f)
        return d


class PassValue(InputFieldsMixin):
    """Base class for `pass_value` attributes.
    """
    def __init__(self, **input_data):
        self.input_data = input_data

    def get(self):
        raise NotImplementedError(
            'PassValue must implement `.get()` method')


class BaseExpectation(InputFieldsMixin):
    """Base class for Expectation execution classes.
    """
    def __init__(self, dataframe, pass_value, **input_data):
        self.dataframe = dataframe
        self.pass_value = pass_value
        self.input_data = input_data

    @property
    def pass_value(self):
        return self._pass_value

    @pass_value.setter
    def pass_value(self, d):
        if not isinstance(d, PassValue):
            raise AttributeError(
                'pass_value must be of type: PassValue')
        self._pass_value = d

    @property
    def observed_value(self):
        if not hasattr(self, '_observed_value'):
            raise AttributeError(
                'Must run the `.do_check()` method to access `observed_value` property.')
        return self._observed_value

    @property
    def expected_value(self):
        if not hasattr(self, '_expected_value'):
            self._expected_value = self.pass_value.get()
        return self._expected_value

    @property
    def passed(self):
        if not hasattr(self, '_passed'):
            raise AttributeError(
                'Must run the `.do_check()` method to access `passed` property.')
        return self._passed

    def get_observed_value(self):
        raise NotImplementedError(
            'Expectation must implement `.get_observed_value()` method')

    def evaluate(self, observed_value, pass_value):
        raise NotImplementedError(
            'Expectation must implement `.evaluate(observed_value, pass_value)` method')

    def do_check(self):
        """Execute the check against the provided dataframe.
        """
        self._observed_value = self.get_observed_value()
        self._passed = self.evaluate(self.observed_value, self.expected_value)
