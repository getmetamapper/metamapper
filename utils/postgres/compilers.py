# -*- coding: utf-8 -*-
from django.core.exceptions import SuspiciousOperation
from django.db.models import Model
from django.db.models.fields.related import RelatedField
from django.db.models.sql.compiler import SQLInsertCompiler, SQLUpdateCompiler
from django.db.utils import ProgrammingError

from utils.postgres.expressions import HStoreValue


class PostgresUpdateCompiler(SQLUpdateCompiler):
    """Compiler for SQL UPDATE statements that return the
    primary keys of the affected rows.
    """
    def as_sql(self):
        self._prepare_query_values()
        return super().as_sql()

    def _prepare_query_values(self):
        """Extra prep on query values by converting dictionaries into.
        :see:HStoreValue expressions.
        This allows putting expressions in a dictionary. The
        :see:HStoreValue will take care of resolving the expressions
        inside the dictionary.
        """
        new_query_values = []
        for field, model, val in self.query.values:
            if isinstance(val, dict):
                val = HStoreValue(val)
            new_query_values.append((field, model, val))
        self.query.values = new_query_values


class PostgresInsertCompiler(SQLInsertCompiler):
    """Compiler for SQL INSERT statements.
    """
    def __init__(self, *args, **kwargs):
        """Initializes a new instance of :see:PostgresInsertCompiler.
        """
        super().__init__(*args, **kwargs)
        self.qn = self.connection.ops.quote_name

    def as_sql(self, return_id=False):
        """Builds the SQL INSERT statement.
        """
        queries = [
            self._rewrite_insert(sql, params, return_id)
            for sql, params in super().as_sql()
        ]
        return queries

    def execute_sql(self, return_id=False):
        # execute all the generate queries
        with self.connection.cursor() as cursor:
            rows = []
            for sql, params in self.as_sql(return_id):
                cursor.execute(sql, params)
                try:
                    rows.extend(cursor.fetchall())
                except ProgrammingError:
                    pass

        # create a mapping between column names and column value
        return [
            {
                column.name: row[column_index]
                for column_index, column in enumerate(cursor.description)
                if row
            }
            for row in rows
        ]

    def _rewrite_insert(self, sql, params, return_id=False):
        """Rewrites a formed SQL INSERT query to include the ON CONFLICT clause.

        Arguments:
            sql:
                The SQL INSERT query to rewrite.
            params:
                The parameters passed to the query.
            returning:
                What to put in the `RETURNING` clause
                of the resulting query.
        Returns:
            A tuple of the rewritten SQL query and new params.
        """
        returning = (
            self.qn(self.query.model._meta.pk.attname) if return_id else "*"
        )

        return self._rewrite_insert_on_conflict(
            sql, params, self.query.conflict_action.value, returning
        )

    def _rewrite_insert_on_conflict(self, sql, params, conflict_action, returning):
        """Rewrites a normal SQL INSERT query to add the 'ON CONFLICT' clause.
        """
        update_columns = ", ".join(
            [
                "{0} = EXCLUDED.{0}".format(self.qn(field.column))
                for field in self.query.update_fields
            ]
        )

        # build the conflict target, the columns to watch
        # for conflicts
        conflict_target = self._build_conflict_target()
        index_predicate = self.query.index_predicate

        sql_template = (
            "{insert} ON CONFLICT {conflict_target} DO {conflict_action}"
        )

        if index_predicate:
            sql_template = "{insert} ON CONFLICT {conflict_target} WHERE {index_predicate} DO {conflict_action}"

        if conflict_action == "UPDATE":
            sql_template += " SET {update_columns}"

        sql_template += " RETURNING {returning}"

        return (
            sql_template.format(
                insert=sql,
                conflict_target=conflict_target,
                conflict_action=conflict_action,
                update_columns=update_columns,
                returning=returning,
                index_predicate=index_predicate,
            ),
            params,
        )

    def _build_conflict_target(self):
        """Builds the `conflict_target` for the ON CONFLICT clause.
        """
        conflict_target = []

        if not isinstance(self.query.conflict_target, list):
            raise SuspiciousOperation(
                (
                    "%s is not a valid conflict target, specify "
                    "a list of column names, or tuples with column "
                    "names and hstore key."
                )
                % str(self.query.conflict_target)
            )

        def _assert_valid_field(field_name):
            field_name = self._normalize_field_name(field_name)
            if self._get_model_field(field_name):
                return

            raise SuspiciousOperation(
                (
                    "%s is not a valid conflict target, specify "
                    "a list of column names, or tuples with column "
                    "names and hstore key."
                )
                % str(field_name)
            )

        for field_name in self.query.conflict_target:
            _assert_valid_field(field_name)

            # special handling for hstore keys
            if isinstance(field_name, tuple):
                conflict_target.append(
                    "(%s->'%s')"
                    % (self._format_field_name(field_name), field_name[1])
                )
            else:
                conflict_target.append(self._format_field_name(field_name))

        return "(%s)" % ",".join(conflict_target)

    def _get_model_field(self, name):
        """Gets the field on a model with the specified name.
        Arguments:
            name:
                The name of the field to look for.
                This can be both the actual field name, or
                the name of the column, both will work :)
        Returns:
            The field with the specified name or None if
            no such field exists.
        """
        field_name = self._normalize_field_name(name)
        # 'pk' has special meaning and always refers to the primary
        # key of a model, we have to respect this de-facto standard behaviour
        if field_name == "pk" and self.query.model._meta.pk:
            return self.query.model._meta.pk

        for field in self.query.model._meta.local_concrete_fields:
            if field.name == field_name or field.column == field_name:
                return field

        return None

    def _format_field_name(self, field_name):
        """Formats a field's name for usage in SQL.
        Arguments:
            field_name:
                The field name to format.
        Returns:
            The specified field name formatted for
            usage in SQL.
        """
        field = self._get_model_field(field_name)
        return self.qn(field.column)

    def _format_field_value(self, field_name):
        """Formats a field's value for usage in SQL.
        Arguments:
            field_name:
                The name of the field to format
                the value of.
        Returns:
            The field's value formatted for usage
            in SQL.
        """
        field_name = self._normalize_field_name(field_name)
        field = self._get_model_field(field_name)

        value = getattr(self.query.objs[0], field.attname)

        if isinstance(field, RelatedField) and isinstance(value, Model):
            value = value.pk

        return SQLInsertCompiler.prepare_value(
            self,
            field,
            # Note: this deliberately doesn't use `pre_save_val` as we don't
            # want things like auto_now on DateTimeField (etc.) to change the
            # value. We rely on pre_save having already been done by the
            # underlying compiler so that things like FileField have already had
            # the opportunity to save out their data.
            value,
        )

    def _normalize_field_name(self, field_name):
        """Normalizes a field name into a string by extracting the field name
        if it was specified as a reference to a HStore key (as a tuple).
        Arguments:
            field_name:
                The field name to normalize.
        Returns:
            The normalized field name.
        """
        if isinstance(field_name, tuple):
            field_name, _ = field_name

        return field_name
