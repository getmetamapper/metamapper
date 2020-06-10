# -*- coding: utf-8 -*-
import graphene

import utils.shortcuts as shortcuts

from app.authorization.fields import AuthConnectionField

from app.comments.models import Comment
from app.comments.schema import CommentType

from django.db.models import F
from app.authorization.permissions import login_required


class Query(graphene.ObjectType):
    """Queries related to the comments models.
    """
    comments = AuthConnectionField(
        type=CommentType,
        object_id=graphene.ID(required=True),
    )

    @login_required
    def resolve_comments(self, info, object_id, *args, **kwargs):
        """Retrieve a list of comments associated with the provided object.
        """
        _type, object_id = shortcuts.from_global_id(object_id)

        content_type = Comment.get_content_type_from_node(_type)

        filter_kwargs = {
            'workspace': info.context.workspace,
            'object_id': object_id,
            'parent_id': None,
            'content_type': content_type,
        }

        return Comment.objects.filter(**filter_kwargs).order_by(
            F('pinned_at').desc(nulls_last=True),
            F('created_at').asc(),
        )
