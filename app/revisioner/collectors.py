# -*- coding: utf-8 -*-
from app.definitions.models import Table, Column, Index
from app.revisioner.revisioners import get_content_types


class ObjectCollector(object):
    """Handles management of one type of DB object.
    """
    def __init__(self, collection):
        self.collection = list(collection)
        self._processed = set()

    @property
    def processed(self):
        return self.all(self.collection, lambda o: o.pk in self._processed)

    @property
    def assigned(self):
        return self.processed

    @property
    def unassigned(self):
        return self.all(self.collection, lambda o: o.pk not in self._processed)

    def find_by_pk(self, pk):
        """Search the collection by the provided OID.
        """
        if not pk:
            return None
        return self.find_by(lambda o: str(o.pk) == str(pk))

    def find_by_oid(self, object_id, unassigned_only=False):
        """Search the collection by the provided OID.
        """
        if not object_id:
            return None
        return self.find_by(lambda o: str(o.object_id) == str(object_id), unassigned_only)

    def find_by_name(self, name, unassigned_only=False):
        """Search the collection by the provided asset name.
        """
        if not name:
            return None
        return self.find_by(lambda o: str(o.name) == str(name), unassigned_only)

    def find_by_revision(self, revision_id, unassigned_only=False):
        """Search the collection by the provided asset revision id.
        """
        if not revision_id:
            return None
        return self.find_by(lambda o: str(o.created_revision_id) == str(revision_id), unassigned_only)

    def search_unassigned(self, func):
        """Search unassigned list.
        """
        return self.find_by(func, True)

    def find_by(self, func, unassigned_only=False):
        """Search the collection by a lambda function.
        """
        if unassigned_only:
            collection = self.unassigned
        else:
            collection = self.collection
        result = self.first(collection, func)
        if result:
            return result

    def mark_as_processed(self, pk):
        """Mark a record as processed.
        """
        self._processed.add(pk)

    def first(self, collection, func):
        return next(filter(func, collection), None)

    def all(self, collection, func):
        return list(filter(func, collection))


class DefinitionCollector(object):
    """docstring for DefinitionCollector
    """
    def __init__(self, datastore, *args, **kwargs):
        self.datastore = datastore
        self.workspace = self.datastore.workspace
        self.content_types = get_content_types()
        self.schemas = ObjectCollector(
            self.datastore.schemas.all()
        )
        self.tables = ObjectCollector(
            Table.objects.filter(schema__datastore_id=self.datastore.id).select_related('schema')
        )
        self.columns = ObjectCollector(
            Column.objects.filter(table__schema__datastore_id=self.datastore.id).select_related('table')
        )
        self.indexes = ObjectCollector(
            Index.objects.filter(table__schema__datastore_id=self.datastore.id).select_related('table')
        )

    @property
    def mapper(self):
        """Mapping of all database objects.
        """
        return {
            'Column': self.columns,
            'Index': self.indexes,
            'Schema': self.schemas,
            'Table': self.tables,
        }

    @property
    def unassigned(self):
        """Mapping of unassigned database objects. Usually indicates DROPPED objects.
        """
        return {k: v.unassigned for k, v in self.mapper.items()}

    def has_unassigned(self, object_type=None):
        """Boolean check to see if unassigned objects exist.
        """
        if object_type:
            return len(self.unassigned[object_type]) > 0
        return any([len(u) > 0 for u in self.unassigned.values()])

    def find_by_revision(self, revision_id, content_type=None):
        """Search cache by creation revision.
        """
        for name, collector in self.mapper.items():
            if content_type and content_type != self.content_types[name]:
                continue
            resource = collector.find_by_revision(revision_id)
            if resource:
                return resource
