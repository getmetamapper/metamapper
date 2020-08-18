# -*- coding: utf-8 -*-
from django.utils.functional import cached_property

from app.authentication.loaders import UserLoader, WorkspaceLoader
from app.definitions.loaders import SchemaTableLoader, TableColumnLoader, IndexColumnLoader, TableSchemaLoader
from app.comments.loaders import ColumnCommentCountLoader, ChildCommentLoader
from app.revisioner.loaders import RelatedRevisionResourceLoader
from app.omnisearch.loaders import OmnisearchResultLoader


class GlobalDataLoader(object):
    """Container object for all data loaders. This allows data loaders
    to be accessible from the Graphene context.
    """
    def __init__(self, request):
        self.request = request

    @cached_property
    def user(self):
        return self.request.user

    @cached_property
    def workspaces(self):
        return WorkspaceLoader()

    @cached_property
    def users(self):
        return UserLoader()

    @cached_property
    def related_revision_resources(self):
        return RelatedRevisionResourceLoader()

    @cached_property
    def schema_tables(self):
        return SchemaTableLoader()

    @cached_property
    def table_schemas(self):
        return TableSchemaLoader()

    @cached_property
    def table_columns(self):
        return TableColumnLoader()

    @cached_property
    def index_columns(self):
        return IndexColumnLoader()

    @cached_property
    def column_comment_counts(self):
        return ColumnCommentCountLoader()

    @cached_property
    def child_comments(self):
        return ChildCommentLoader()

    @cached_property
    def omnisearch_results(self):
        return OmnisearchResultLoader()
