# -*- coding: utf-8 -*-
import operator
import metamapper.fields as fields

from app.checks.tasks.base import BaseExpectation

from utils.shortcuts import get_module_class_validator, load_class


__all__ = [
    'AssertRowCountToBe',
    'AssertCountOfDuplicateValuesOfColumnToBe',
    'AssertFirstValueOfColumnToBe',
    'AssertAvgValueOfColumnToBe',
    'AssertMinValueOfColumnToBe',
    'AssertMaxValueOfColumnToBe',
]

OPERATOR_MAPPING = {
    'equal to': operator.eq,
    'not equal to': operator.ne,
    'greater than': operator.gt,
    'greater than or equal to': operator.ge,
    'less than': operator.lt,
    'less than or equal to': operator.le,
}

OPERATOR_CHOICES = [k for k in OPERATOR_MAPPING.keys()]


validator = get_module_class_validator(__name__, __all__)


def get_handler_configuration_options():
    """Return the configuration options for each handler.
    """
    output = []
    for handler_class in __all__:
        handler = load_class(__name__, handler_class)
        handler_fields = handler.get_fields()
        handler_kwargs = {
            'name': getattr(handler.Meta, 'name', None),
            'info': getattr(handler.Meta, 'info', None),
            'handler': '.'.join([__name__, handler_class]),
            'details': [
                {
                    'name': name,
                    'type': field.__class__.__name__,
                    'label': field.label,
                    'options': field.get_options(),
                    'help_text': field.help_text,
                }
                for name, field in handler_fields
            ],
        }
        output.append(handler_kwargs)
    return output


class AssertColumnToBe(BaseExpectation):
    """Base class for expectations related to column operations.
    """
    class Input:
        column = fields.ColumnField(
            label='Column',
            max_length=255,
            help_text='The query column name to use in the expectation.')
        op = fields.ChoiceField(
            label='Operation',
            choices=OPERATOR_CHOICES,
            help_text='The operation to use when comparing the outputted and expected values.')
        skipna = fields.BooleanField(
            label='Skip NULLs',
            default=True,
            help_text='Remove NULL values from result prior to testing.')

    def get_observed_value(self):
        col = self.inputs['column']
        if col not in self.dataframe.columns or self.dataframe.empty:
            return None
        return self._get_observed_value(col)

    def evaluate(self, observed_value, expected_value):
        if observed_value is None and expected_value is not None:
            return False
        return OPERATOR_MAPPING[self.inputs['op']](observed_value, expected_value)


class AssertRowCountToBe(BaseExpectation):
    """Check the row count of the dataframe against the pass value.
    """
    class Input:
        op = fields.ChoiceField(
            label='Operation',
            choices=OPERATOR_CHOICES,
            help_text='The operation to use when comparing the outputted and expected values.')

    class Meta:
        name = 'Row Count'
        info = 'Compare against the total number of records returned'
        desc = 'Expect the row count to be {{ op }}'

    def get_observed_value(self):
        return self.dataframe.shape[0]

    def evaluate(self, observed_value, expected_value):
        return OPERATOR_MAPPING[self.inputs['op']](observed_value, expected_value)


class AssertFirstValueOfColumnToBe(AssertColumnToBe):
    """Check the first value of the dataframe against the pass value.
    """
    class Input:
        column = fields.ColumnField(
            label='Column',
            max_length=255,
            help_text='The query column name to use in the expectation.')
        op = fields.ChoiceField(
            label='Operation',
            choices=OPERATOR_CHOICES,
            help_text='The operation to use when comparing the outputted and expected values.')

    class Meta:
        name = 'First Value'
        info = 'Compare against the first value seen of a column'
        desc = 'Expect the first value of the `{{ column }}` column to be {{ op }}'

    def _get_observed_value(self, column):
        return self.dataframe[column].iloc[0]


class AssertAvgValueOfColumnToBe(AssertColumnToBe):
    """Check the average value of the dataframe against the pass value.
    """
    class Meta:
        name = 'Average'
        info = 'Compare against the average value of a column'
        desc = 'Expect the average of the `{{ column }}` column to be {{ op }}'

    def _get_observed_value(self, column):
        return self.dataframe[column].mean(skipna=self.inputs['skipna'])


class AssertMaxValueOfColumnToBe(AssertColumnToBe):
    """Check the average value of the dataframe against the pass value.
    """
    class Meta:
        name = 'Maximum'
        info = 'Compare against the maximum value of a column'
        desc = 'Expect the max of the `{{ column }}` column to be {{ op }}'

    def _get_observed_value(self, column):
        return self.dataframe[column].max(skipna=self.inputs['skipna'])


class AssertMinValueOfColumnToBe(AssertColumnToBe):
    """Check the average value of the dataframe against the pass value.
    """
    class Meta:
        name = 'Minimum'
        info = 'Compare against the minimum value of a column'
        desc = 'Expect the min of the `{{ column }}` column to be {{ op }}'

    def _get_observed_value(self, column):
        return self.dataframe[column].min(skipna=self.inputs['skipna'])


class AssertCountOfDuplicateValuesOfColumnToBe(AssertColumnToBe):
    """Compare against the count of duplicate values in a column.
    """
    class Input:
        columns = fields.ColumnsField(
            label='Columns',
            child=fields.ColumnField(max_length=255),
            help_text='The query column name to use in the expectation.')
        op = fields.ChoiceField(
            label='Operation',
            choices=OPERATOR_CHOICES,
            help_text='The operation to use when comparing the outputted and expected values.')
        skipna = fields.BooleanField(
            label='Skip NULLs',
            default=True,
            help_text='Remove NULL values from result prior to testing.')

    class Meta:
        name = 'Duplicate Rows'
        info = 'Compare against the count of unique duplicate rows'
        desc = 'Expect the count of unique duplicate values of the `{{ columns | join(",") }}` column(s) to be {{ op }}'

    def get_observed_value(self):
        columns = self.inputs['columns']
        if self.dataframe.empty:
            return None
        if any(col not in self.dataframe.columns for col in columns):
            return None
        return self._get_observed_value(columns)

    def evaluate(self, observed_value, expected_value):
        if observed_value is None and expected_value is not None:
            return False
        return OPERATOR_MAPPING[self.inputs['op']](observed_value, expected_value)

    def _get_observed_value(self, columns):
        df = self.dataframe[columns]
        if self.inputs['skipna']:
            df = df.dropna()
        df = df.value_counts()
        return df[df > 1].shape[0]
