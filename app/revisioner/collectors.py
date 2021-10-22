# -*- coding: utf-8 -*-
from app.definitions.models import Schema, Table, Column, Index
from utils.contenttypes import get_content_types


class SingleValueLookupObjectCollector(object):
    """Handles management of one type of DB object.
    """
    def __init__(self, collection, autotrack_processed=True):
        self.collection = collection
        self._processed = set()
        self.autotrack_processed = autotrack_processed

    @property
    def processed(self):
        return self.assigned

    @property
    def assigned(self):
        return self.collection.filter(pk__in=self._processed)

    @property
    def unassigned(self):
        return self.collection.exclude(pk__in=self._processed)

    def find_by_pk(self, id):
        """Search the collection by the provided ident.
        """
        if not id:
            return None
        return self.find_by(id=id)

    def find_by_oid(self, object_id):
        """Search the collection by the provided OID.
        """
        if not object_id:
            return None
        return self.find_by(object_id=object_id)

    def find_by_name(self, name):
        """Search the collection by the provided asset name.
        """
        if not name:
            return None
        return self.find_by(name=name)

    def find_by_revision(self, revision_id):
        """Search the collection by the provided asset revision id.
        """
        if not revision_id:
            return None
        return self.collection.filter(created_revision_id=revision_id).first()

    def search_unassigned(self, **kwargs):
        """Search unassigned list.
        """
        resource = self.collection.filter(**kwargs).first()
        if resource and resource.pk not in self._processed:
            if self.autotrack_processed:
                self.mark_as_processed(resource.pk)
            return resource

    def find_by(self, **kwargs):
        resource = self.collection.filter(**kwargs).first()
        if resource and self.autotrack_processed:
            self.mark_as_processed(resource.pk)
        return resource

    def mark_as_processed(self, pk):
        """Mark a record as processed.
        """
        self._processed.add(pk)


class InMemoryLookupObjectCollector(object):
    """Handles management of one type of DB object.
    """
    def __init__(self, collection, autotrack_processed=True):
        self.collection = list(collection)
        self._processed = set()
        self.autotrack_processed = autotrack_processed

    @property
    def processed(self):
        return self.assigned

    @property
    def assigned(self):
        return list(filter(lambda o: o.pk in self._processed, self.collection))

    @property
    def unassigned(self):
        return list(filter(lambda o: o.pk not in self._processed, self.collection))

    def find_by_pk(self, id):
        """Search the collection by the provided ident.
        """
        if not id:
            return None
        return self.find_by(id=id)

    def find_by_oid(self, object_id):
        """Search the collection by the provided OID.
        """
        if not object_id:
            return None
        return self.find_by(object_id=object_id)

    def find_by_name(self, name):
        """Search the collection by the provided asset name.
        """
        if not name:
            return None
        return self.find_by(name=name)

    def find_by_revision(self, revision_id):
        """Search the collection by the provided asset revision id.
        """
        if not revision_id:
            return None
        return self.find_by(lambda o: str(o.created_revision_id) == str(revision_id))

    def search_unassigned(self, **kwargs):
        """Search unassigned list.
        """
        resource = self.first(**kwargs)
        if resource and resource.pk not in self._processed:
            if self.autotrack_processed:
                self.mark_as_processed(resource.pk)
            return resource

    def find_by(self, **kwargs):
        resource = self.first(**kwargs)
        if resource and self.autotrack_processed:
            self.mark_as_processed(resource.pk)
        return resource

    def mark_as_processed(self, pk):
        """Mark a record as processed.
        """
        self._processed.add(pk)

    def first(self, **kwargs):
        return next(self._filter(**kwargs), None)

    def all(self, **kwargs):
        return list(self._filter(**kwargs))

    def _filter(self, **kwargs):
        return filter(lambda c: all(str(getattr(c, k, None)) == str(v) for k, v in kwargs.items()), self.collection)


class DefinitionCollector(object):
    """Class to manage look-up to datastore assets.
    """
    def __init__(self, datastore, *args, **kwargs):
        self.datastore = datastore
        self.workspace = self.datastore.workspace
        self.content_types = get_content_types()
        self.schemas = SingleValueLookupObjectCollector((
            Schema.all_objects
                  .filter(datastore_id=self.datastore.id)
                  .only('pk', 'object_id', 'name')
        ))
        self.tables = SingleValueLookupObjectCollector((
            Table.all_objects
                 .filter(schema__datastore_id=self.datastore.id)
                 .select_related('schema')
                 .only('pk', 'object_id', 'name', 'schema')
        ))
        self.columns = SingleValueLookupObjectCollector((
            Column.all_objects
                  .filter(table__schema__datastore_id=self.datastore.id)
                  .select_related('table')
                  .only('pk', 'object_id', 'name', 'table')
        ))
        self.indexes = SingleValueLookupObjectCollector((
            Index.objects
                 .filter(table__schema__datastore_id=self.datastore.id)
                 .select_related('table')
                 .only('pk', 'object_id', 'name', 'table')
        ))

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

    def find_by_revision(self, revision_id, content_type=None):
        """Search cache by creation revision.
        """
        for name, collector in self.mapper.items():
            if content_type and content_type != self.content_types[name]:
                continue
            resource = collector.find_by_revision(revision_id)
            if resource:
                return resource
