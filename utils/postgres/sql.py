# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.core.exceptions import SuspiciousOperation
from django.contrib.postgres.search import SearchQuery
from django.db import connections
from django.db.models import sql
from django.db.models.constants import LOOKUP_SEP

from utils.postgres.types import ConflictAction
from utils.postgres.compilers import PostgresUpdateCompiler, PostgresInsertCompiler


class PostgresQuery(sql.Query):
    """PostgresQuery class.
    """
    def chain(self, klass=None):
        """Chains this query to another.

        We override this so that we can make sure our subclassed query
        classes are used.
        """
        if klass == sql.UpdateQuery:
            return super().chain(PostgresUpdateQuery)
        if klass == sql.InsertQuery:
            return super().chain(PostgresInsertQuery)
        return super().chain(klass)

    def rename_annotations(self, annotations):
        """Renames the aliases for the specified annotations:
            .annotate(myfield=F('somestuf__myfield'))
            .rename_annotations(myfield='field')

        Arguments:
            annotations:
                The annotations to rename. Mapping the
                old name to the new name.
        """
        for old_name, new_name in annotations.items():
            annotation = self.annotations.get(old_name)
            if not annotation:
                raise SuspiciousOperation(
                    (
                        'Cannot rename annotation "{old_name}" to "{new_name}", because there'
                        ' is no annotation named "{old_name}".'
                    ).format(old_name=old_name, new_name=new_name)
                )
            self._annotations = OrderedDict(
                [
                    (new_name, v) if k == old_name else (k, v)
                    for k, v in self._annotations.items()
                ]
            )

    def add_fields(self, field_names, allow_m2m):
        """Adds the given (model) fields to the select set. The field names are
        added in the order specified.

        This overrides the base class's add_fields method. This is called by
        the .values() or .values_list() method of the query set. It instructs
        the ORM to only select certain values. A lot of processing is neccesarry
        because it can be used to easily do joins. For example, `my_fk__name` pulls
        in the `name` field in foreign key `my_fk`.

        In our case, we want to be able to do `title__en`, where `title` is a HStoreField
        and `en` a key. This doesn't really involve a join. We iterate over the specified
        field names and filter out the ones that refer to HStoreField and compile it into
        an expression which is added to the list of to be selected fields using `self.add_select`.
        """
        alias = self.get_initial_alias()
        opts = self.get_meta()
        cols = []
        for name in field_names:
            parts = name.split(LOOKUP_SEP)
            join_info = self.setup_joins(
                parts, opts, alias, allow_many=allow_m2m
            )
            targets, final_alias, joins = self.trim_joins(
                join_info[1], join_info[3], join_info[4]
            )
            for target in targets:
                cols.append(target.get_col(final_alias))
        if cols:
            self.set_select(cols)


class PostgresInsertQuery(sql.InsertQuery):
    """Insert query using PostgreSQL.
    """
    def __init__(self, *args, **kwargs):
        """Initializes a new instance :see:PostgresInsertQuery."""

        super(PostgresInsertQuery, self).__init__(*args, **kwargs)

        self.conflict_target = []
        self.conflict_action = ConflictAction.UPDATE

        self.update_fields = []

    def values(self, objs, insert_fields, update_fields):
        """Sets the values to be used in this query.
        Insert fields are fields that are definitely
        going to be inserted, and if an existing row
        is found, are going to be overwritten with the
        specified value.
        Update fields are fields that should be overwritten
        in case an update takes place rather than an insert.
        If we're dealing with a INSERT, these will not be used.
        Arguments:
            objs:
                The objects to apply this query to.
            insert_fields:
                The fields to use in the INSERT statement
            update_fields:
                The fields to only use in the UPDATE statement.
        """
        self.insert_values(insert_fields, objs, raw=False)
        self.update_fields = update_fields

    def get_compiler(self, using=None, connection=None):
        if using:
            connection = connections[using]
        return PostgresInsertCompiler(self, connection, using)


class PostgresUpdateQuery(sql.UpdateQuery):
    """Update query using PostgreSQL.
    """
    def get_compiler(self, using=None, connection=None):
        if using:
            connection = connections[using]
        return PostgresUpdateCompiler(self, connection, using)


class PostgresOrSearchQuery(SearchQuery):
    """Extension of SearchQuery to perform OR instead of AND operator.
    """
    def as_sql(self, compiler, connection, function=None, template=None):
        """Override `.as_sql` to add extended OR search capabilities.
        """
        sql, params = super().as_sql(compiler, connection, function, template)

        if not self.config:
            fcn = function or self.function
            sql = "replace({}(%s)::text, '&', '|')::tsquery".format(fcn)
        else:
            config_sql, config_params = compiler.compile(self.config)
            template = '{}({}::regconfig, %s)'.format(function, config_sql)
            sql = template % sql
            params = config_params + params

        if self.invert:
            sql = '!!(%s)' % sql

        return sql, params
