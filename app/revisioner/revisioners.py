# -*- coding: utf-8 -*-
import json
import hashlib

from django.db.models import F
from django.utils.functional import cached_property

from utils.shortcuts import dict_list_eq
from utils.contenttypes import get_content_type_for_model

from app.revisioner.models import Revision
from app.revisioner.collectors import DefinitionCollector
from app.revisioner.decorators import (
    track_revised_properties, on_modify_property
)
from app.definitions.models import Schema, Table, Column, Index


class RevisionMixin(object):
    """Shared functionality for Revision classes.
    """
    action_type = None

    def __init__(self,
                 resource_type,
                 resource,
                 parent_resource=None,
                 parent_resource_revision=None,
                 *args,
                 **kwargs):
        self.resource_type = resource_type
        self.resource = resource
        self.parent_resource = parent_resource
        self.parent_resource_revision = parent_resource_revision

    @property
    def resource_id(self):
        """Get the resource ID if the resource exists.
        """
        return self.resource.pk if self.resource else None

    @property
    def parent_resource_id(self):
        """Get the  parent resource ID if the  parent resource exists.
        """
        return self.parent_resource.pk if self.parent_resource else None

    @property
    def parent_resource_type(self):
        """Get the parent resource content type if the parent resource exists.
        """
        if not self.parent_resource:
            return None
        return get_content_type_for_model(self.parent_resource.__class__)

    @property
    def parent_resource_type_id(self):
        """Get the parent resource content type if the parent resource exists.
        """
        return self.parent_resource.pk if self.parent_resource_type else None

    @property
    def parent_resource_revision_id(self):
        if not self.parent_resource_revision:
            return None
        return self.parent_resource_revision.revision_id

    @property
    def revision_id(self):
        """Revision is a SHA1 checksum of all the relevant properties.
        """
        checksum_dict = {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type.id,
            'parent_resource_id': self.parent_resource_id,
            'parent_resource_type': self.parent_resource_type_id,
            'action': self.action_type,
            'metadata': self.get_metadata(),
        }
        if self.parent_resource_revision_id:
            checksum_dict['parent_resource_revision_id'] = self.parent_resource_revision_id
        return hashlib.sha1(
            json.dumps(checksum_dict, sort_keys=True).encode('utf-8'),
        ).hexdigest()

    def set_metadata(self, **metadata):
        """Simple `set` method for metadata.
        """
        self.metadata = metadata

    def get_metadata(self):
        """Simple `get` method for metadata.
        """
        return self.metadata

    def as_dict(self):
        """Returns revision as a dictionary.
        """
        return {
            'revision_id': self.revision_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'parent_resource_revision_id': self.parent_resource_revision_id,
            'parent_resource_id': self.parent_resource_id,
            'parent_resource_type': self.parent_resource_type,
            'metadata': self.get_metadata(),
            'action': self.action_type,
        }


class OnCreateRevision(RevisionMixin):
    """Create dictionary representation of a CREATED revision.
    """
    action_type = Revision.CREATED


class OnModifyRevision(RevisionMixin):
    """Create dictionary representation of a MODIFIED revision.
    """
    action_type = Revision.MODIFIED


class OnDroppedRevision(RevisionMixin):
    """Create dictionary representation of a DROPPED revision.
    """
    action_type = Revision.DROPPED

    @property
    def resource_id(self):
        """We need to have the PK to drop a record.
        """
        return self.resource.pk

    def get_metadata(self):
        """No metadata for DROPPED resources.
        """
        return {}


class Revisioner(object):
    """Core revisioner class. Detects and logs Revision objects
    based on metadata sourced by Inspector.
    """
    created_fields = []

    modified_fields = []

    resource_type = None

    def __init__(self, instance, parent_resource=None, parent_resource_revision=None):
        self.instance = instance
        self.parent_resource = parent_resource
        self.parent_resource_revision = parent_resource_revision
        if self.resource_type is None:
            raise NotImplementedError()

    def make_revisions(self, **properties):
        """Get revisions for the provided instance.
        """
        if self.instance:
            return self.make_modified(**properties)
        else:
            return self.make_created(**properties)

    def make_created(self, **properties):
        """Get revisions for a CREATED action. Returns a <List(OnCreateRevision)> type.
        """
        revision = OnCreateRevision(
            resource=self.instance,
            resource_type=self.resource_type,
            parent_resource=self.parent_resource,
            parent_resource_revision=self.parent_resource_revision,
        )
        metadata = {
            f: properties.get(f)
            for f in self.created_fields
        }
        revision.set_metadata(**metadata)
        return [revision]

    def make_modified(self, **properties):
        """Get revisions for a MODIFIED action. Returns a <List(OnModifyRevision)> type.
        """
        revisions = []
        for property_function in self.on_modify:
            revisions += property_function(self, **properties)
        return revisions

    def make_dropped(self, **properties):
        """Get revisions for a DROPPED action. Returns a <List(OnDroppedRevision)> type.
        """
        revision = OnDroppedRevision(
            resource=self.instance,
            resource_type=self.resource_type,
            parent_resource=self.parent_resource,
            parent_resource_revision=self.parent_resource_revision,
        )
        return [revision]

    def get_modify_revision(self, field, old_value, new_value):
        """Helper function for grabbing MODIFIED revisions.
        """
        revision = OnModifyRevision(
            resource=self.instance,
            resource_type=self.resource_type,
            parent_resource=self.parent_resource,
            parent_resource_revision=self.parent_resource_revision,
        )
        metadata = {
            'field': field,
            'old_value': old_value,
            'new_value': new_value,
        }
        revision.set_metadata(**metadata)
        return revision

    @on_modify_property
    def modified_tracked_fields(self, **properties):
        """Detected changes for `modified_fields` list at class-level. `get_base_modified_fields`
        """
        revisions = []
        for field in self.modified_fields:
            new_value = properties[field]
            old_value = getattr(self.instance, field)
            if str(old_value) == str(new_value):
                continue
            revision = self.get_modify_revision(field, old_value, new_value)
            revisions.append(revision)
        return revisions


@track_revised_properties
class SchemaRevisioner(Revisioner):
    """Revisioner class for Schema objects.
    """
    created_fields = [
        'name',
        'object_id',
    ]

    modified_fields = [
        'name',
        'object_id',
    ]

    @cached_property
    def resource_type(self):
        return get_content_type_for_model(Schema)


@track_revised_properties
class TableRevisioner(Revisioner):
    """Revisioner class for Table objects.
    """
    created_fields = [
        'name',
        'object_id',
        'kind',
    ]

    modified_fields = [
        'name',
        'object_id',
    ]

    @cached_property
    def resource_type(self):
        return get_content_type_for_model(Table)

    @on_modify_property
    def modified_table_schema(self, **properties):
        """Check if the schema has changed.
        """
        new_value = None if not self.parent_resource else self.parent_resource.id
        old_value = self.instance.schema_id

        if old_value == new_value:
            return []

        revision = OnModifyRevision(
            resource=self.instance,
            resource_type=self.resource_type,
            parent_resource=self.parent_resource,
            parent_resource_revision=self.parent_resource_revision,
        )

        metadata = {
            'field': 'schema_id',
            'old_value': old_value,
            'new_value': new_value,
        }
        revision.set_metadata(**metadata)
        return [revision]


@track_revised_properties
class ColumnRevisioner(Revisioner):
    """Revisioner class for Column objects.
    """
    created_fields = [
        'name',
        'object_id',
        'ordinal_position',
        'data_type',
        'max_length',
        'numeric_scale',
        'is_nullable',
        'is_primary',
        'default_value',
        'db_comment',
    ]

    modified_fields = [
        'name',
        'object_id',
        'ordinal_position',
        'data_type',
        'max_length',
        'numeric_scale',
        'is_nullable',
        'is_primary',
        'default_value',
        'db_comment',
    ]

    @cached_property
    def resource_type(self):
        return get_content_type_for_model(Column)


@track_revised_properties
class IndexRevisioner(Revisioner):
    """Revisioner class for Index objects.
    """
    created_fields = [
        'name',
        'object_id',
        'sql',
        'is_primary',
        'is_unique',
        'columns',
    ]

    modified_fields = [
        'name',
        'object_id',
        'sql',
        'is_primary',
        'is_unique',
    ]

    @cached_property
    def resource_type(self):
        return get_content_type_for_model(Index)

    @on_modify_property
    def modified_index_columns(self, **properties):
        """Check if the columns has changed.
        """
        new_value = properties['columns']
        old_value = list(self.instance.index_columns
                                      .annotate(column_name=F('column__name'))
                                      .values('column_name', 'ordinal_position'))

        if dict_list_eq(new_value, old_value):
            return []

        revision = OnModifyRevision(
            resource=self.instance,
            resource_type=self.resource_type,
            parent_resource=self.parent_resource,
            parent_resource_revision=self.parent_resource_revision,
        )

        metadata = {
            'field': 'columns',
            'old_value': old_value,
            'new_value': new_value,
        }

        revision.set_metadata(**metadata)
        return [revision]


def get_revisioner(instance, **kwargs):
    """Get the revisioner associated with the provided model.
    """
    revisioner_map = {
        'Schema': SchemaRevisioner,
        'Table': TableRevisioner,
        'Column': ColumnRevisioner,
        'Index': IndexRevisioner,
    }
    return revisioner_map[instance.__class__.__name__](instance, **kwargs)


def last_revision(list_of_revisions):
    """Get the last item in a list.
    """
    try:
        return list_of_revisions[-1]
    except (IndexError, KeyError):
        return None


def extract_revisions(datastore, definition):
    """Extract changes for a specific schema.
    """
    complete_revisions = []

    collector = DefinitionCollector(datastore)

    schema_metadata = definition['schema']
    schema_instance = schema_metadata.pop('instance')

    if schema_instance:
        schema_instance = collector.schemas.find_by_pk(schema_instance['pk'])

    schema_revisioner = SchemaRevisioner(
        instance=schema_instance,
        parent_resource=datastore,
        parent_resource_revision=None,
    )

    schema_revisions = schema_revisioner.make_revisions(**schema_metadata)
    complete_revisions += schema_revisions

    table_revisions = []

    for t in definition['tables']:
        table_metadata = t.copy()
        table_instance = table_metadata.pop('instance')

        if table_instance:
            table_instance = collector.tables.find_by_pk(table_instance['pk'])

        table_revisioner = TableRevisioner(
            instance=table_instance,
            parent_resource=schema_instance,
            parent_resource_revision=last_revision(schema_revisions),
        )

        columns = table_metadata.pop('columns')
        indexes = table_metadata.pop('indexes')

        table_revisions = table_revisioner.make_revisions(**table_metadata)
        complete_revisions += table_revisions

        last_table_revision = last_revision(table_revisions)

        column_revisions = []
        for c in columns:
            column_metadata = c.copy()
            column_instance = column_metadata.pop('instance')

            if column_instance:
                column_instance = collector.columns.find_by_pk(column_instance['pk'])

            column_revisioner = ColumnRevisioner(
                instance=column_instance,
                parent_resource=table_instance,
                parent_resource_revision=last_table_revision,
            )

            column_revisions = column_revisioner.make_revisions(**column_metadata)
            complete_revisions += column_revisions

        index_revisions = []
        for i in indexes:
            index_metadata = i.copy()
            index_instance = index_metadata.pop('instance')

            if index_instance:
                index_instance = collector.indexes.find_by_pk(index_instance['pk'])

            index_revisioner = IndexRevisioner(
                instance=index_instance,
                parent_resource=table_instance,
                parent_resource_revision=last_table_revision,
            )

            index_revisions = index_revisioner.make_revisions(**index_metadata)
            complete_revisions += index_revisions

    return complete_revisions
