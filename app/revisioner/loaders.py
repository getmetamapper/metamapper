# -*- coding: utf-8 -*-
from collections import defaultdict
from graphene import relay

from promise import Promise
from promise.dataloader import DataLoader

from app.revisioner.models import Revision
from app.revisioner.collectors import DefinitionCollector

from utils.contenttypes import get_content_types


class RelatedRevisionResourceLoader(DataLoader):
    def transform_resource(self, resource):
        """Helper function for preparing the returned object.
        """
        if not resource:
            return None

        klass = resource.__class__.__name__
        _type = '{0}Type'.format(klass)

        related_resource = {
            'id': relay.Node.to_global_id(_type, resource.pk),
            'type': klass,
            'name': resource.name,
            'label': resource.revisioner_label,
            'parent_label': resource.revisioner_parent_label,
            'pathname': resource.revisioner_pathname,
        }

        return related_resource

    def batch_load_fn(self, revision_ids):
        """Batch load all of the necessay resources.
        """
        resources = defaultdict(list)
        revisions = Revision.objects\
                            .filter(revision_id__in=revision_ids)\
                            .prefetch_related('resource')

        if len(revisions):
            datastore = revisions[0].run.datastore
            collector = DefinitionCollector(datastore)

            content_type_mapping = {
                c.id: c
                for _, c in get_content_types().items()
            }

            for revision_id in revision_ids:
                revision = next(filter(lambda r: r.revision_id == revision_id, revisions))
                resource = revision.resource

                content_type = content_type_mapping.get(revision.resource_type_id)

                if not resource:
                    resource = collector.find_by_revision(revision.revision_id, content_type)

                if resource:
                    resources[revision_id] = self.transform_resource(resource)

        return Promise.resolve([resources.get(r) for r in revision_ids])
