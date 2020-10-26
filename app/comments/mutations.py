# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authorization.permissions as permissions
import app.definitions.permissions as definition_permissions

import app.comments.schema as schema
import app.comments.serializers as serializers
import app.omnisearch.tasks as omnisearch

import utils.errors as errors
import utils.mixins.mutations as mixins
import utils.shortcuts as shortcuts


class CreateComment(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Create a parent comment or a nested comment.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanCreateCommentOnDatastore,
    )

    class Input:
        object_id = graphene.ID(required=True)
        parent_id = graphene.ID(required=False)
        html = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.CommentSerializer

    comment = graphene.Field(schema.CommentType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(author=info.context.user)

    @classmethod
    def get_parent(cls, info, parent_id):
        """Get the parent from  a base64 identifier.
        """
        if not parent_id:
            return None
        return cls.get_content_object(info, parent_id)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        """Retrieve appropriate objects for the transaction.
        """
        return {
            "instance": None,
            "data": {
                "content_object": cls.get_content_object(info, data["object_id"]),
                "html": data["html"],
                "parent": cls.get_parent(info, data.get("parent_id")),
            },
            "context": {
                "request": info.context,
            },
        }

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should re-index the object in Elasticsearch immediately.
        """
        return [
            {
                "function": omnisearch.update_single_es_object.delay,
                "arguments": {
                    "index_name": "comment",
                    "instance_id": instance.id,
                },
            }
        ]


class UpdateComment(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Update an existing comment that you created.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanModifyCommentOnDatastore,
    )

    class Input:
        id = graphene.ID(required=True)
        html = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.CommentSerializer

    comment = graphene.Field(schema.CommentType)

    @classmethod
    def get_instance(cls, info, data):
        """Only the author can update the comment.
        """
        instance = relay.Node.get_node_from_global_id(info, data[cls.lookup_field])
        if not instance or instance.author_id != info.context.user.id:
            raise errors.PermissionDenied()
        return instance

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should re-index the object in Elasticsearch immediately.
        """
        return [
            {
                "function": omnisearch.update_single_es_object.delay,
                "arguments": {
                    "index_name": "comment",
                    "instance_id": instance.id,
                },
            }
        ]


class DeleteComment(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Delete an existing comment that you created.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanModifyCommentOnDatastore,
    )

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.CommentSerializer

    @classmethod
    def get_instance(cls, info, data):
        """Only the author can delete the comment.
        """
        instance = relay.Node.get_node_from_global_id(info, data[cls.lookup_field])
        if not instance or instance.author_id != info.context.user.id:
            raise errors.PermissionDenied()
        return instance

    @classmethod
    def tasks_on_success(cls, instance, info):
        """We should re-index the object in Elasticsearch immediately.
        """
        return [
            {
                "function": omnisearch.remove_single_es_object.delay,
                "arguments": {
                    "index_name": "comment",
                    "instance_id": instance._previous_id,
                },
            }
        ]


class TogglePinnedComment(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Pin a parent comment to the top of a thread.
    """
    permission_classes = (
        permissions.WorkspaceWriteAccessOnly,
        definition_permissions.CanModifyCommentOnDatastore,
    )

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.TogglePinCommentSerializer

    comment = graphene.Field(schema.CommentType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(pinned_by=info.context.user)


class VoteForComment(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Submit a vote for a comment if you have not already.
    """
    permission_classes = (permissions.WorkspaceTeamMembersOnly,)

    class Input:
        id = graphene.ID(required=True)
        action = graphene.String(required=True)

    class Meta:
        serializer_class = serializers.VoteForCommentSerializer

    comment = graphene.Field(schema.CommentType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(user=info.context.user)


class UnvoteForComment(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Remove a vote for a comment.
    """
    permission_classes = (permissions.WorkspaceTeamMembersOnly,)

    class Input:
        id = graphene.ID(required=True)

    class Meta:
        serializer_class = serializers.VoteForCommentSerializer

    @classmethod
    def perform_delete(cls, instance, info, **data):
        """Delete the vote for the current user.
        """
        instance.delete_vote(info.context.user)


class Mutation(graphene.ObjectType):
    """Mutations related to the comments models.
    """
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()

    toggle_pinned_comment = TogglePinnedComment.Field()

    vote_for_comment = VoteForComment.Field()
    unvote_for_comment = UnvoteForComment.Field()
