# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import utils.shortcuts as shortcuts

from app.customfields.models import CustomField
from app.customfields.schema import CustomFieldType
from app.customfields.scalars import CustomPropScalar

from app.authorization.fields import AuthConnectionField
from app.authorization.permissions import login_required


class Query(graphene.ObjectType):
    """Queries related to the customfields models.
    """
    custom_properties = graphene.Field(
        type=CustomPropScalar,
        object_id=graphene.ID(required=True),
    )

    custom_fields = AuthConnectionField(
        type=CustomFieldType,
        content_type=graphene.String(required=True),
    )

    @login_required
    def resolve_custom_properties(self, info, object_id, *args, **kwargs):
        """Retrieve custom properties for the provided model instance.
        """
        resource = relay.Node.get_node_from_global_id(info, object_id)

        if not resource or not hasattr(resource, 'custom_properties'):
            return None

        return resource.get_custom_properties()

    @login_required
    def resolve_custom_fields(self, info, content_type, *args, **kwargs):
        """Retrieve specific custom fields attached to a workspace.
        """
        content_type = CustomField.get_content_type_from_name(content_type)
        return info.context.workspace.custom_fields\
                   .filter(content_type=content_type)\
                   .order_by('created_at')
