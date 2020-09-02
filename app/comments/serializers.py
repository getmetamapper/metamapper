# -*- coding: utf-8 -*-
import bleach
import rest_framework.serializers as serializers

import app.audit.decorators as audit

import utils.fields as fields

from app.authentication.models import User
from app.comments.models import Comment
from app.votes.models import Vote

from django.contrib.contenttypes.fields import ContentType

from utils.mixins.serializers import MetamapperSerializer


def get_audit_kwargs(instance):
    """Make the parameters for logging audit activity.
    """
    content_type = ContentType.objects.get_for_model(instance)

    return {
        'target_object_id': instance.object_id,
        'target_content_type_id': instance.content_type_id,
        'action_object_object_id': instance.pk,
        'action_object_content_type_id': content_type.pk,
        'extras': {
            'datastore_id': instance.content_object.datastore_id,
        }
    }


class CommentSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Serializer for interacting with comments.
    """
    html = serializers.CharField(required=True, min_length=1)

    content_object = fields.RelatedObjectField(
        allowed_models=Comment.commentable_types(),
        allow_null=False,
    )

    parent = fields.RelatedObjectField(
        required=False,
        allowed_models=(Comment,),
        allow_null=True,
    )

    def validate_html(self, html):
        """Clean HTML to reduce risk of injection attacks.
        """
        return bleach.clean(html, tags=[
            'del',
            'strong',
            'em',
            'p',
            'a',
            'div',
            'pre',
            'ul',
            'ol',
            'li',
            'br',
        ])

    class Meta:
        model = Comment
        fields = (
            'content_object',
            'html',
            'parent',
        )

    @audit.capture_activity(
        verb='commented on',
        hydrater=get_audit_kwargs,
    )
    def create(self, validated_data):
        """Create a comment using the provided data.
        """
        return Comment.objects.create(**validated_data)

    @audit.capture_activity(
        verb='updated comment on',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Perform the update on the comment instance.
        """
        instance.html = validated_data.get('html', instance.html)
        return instance


class TogglePinCommentSerializer(MetamapperSerializer, serializers.Serializer):
    """Ability to (un)pin a comment to the top of the list.
    """
    class Meta:
        model = Comment

    def save(self, pinned_by):
        """Perform the update if the instance is not already pinned.
        """
        if not isinstance(pinned_by, User):
            raise serializers.ValidationError('User is not valid.')
        if self.instance.pinned:
            self.instance.unpin()
        else:
            self.instance.pin(pinned_by)
        return self.instance


class VoteForCommentSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Serializer for interacting with votes for comments.
    """
    action = serializers.ChoiceField(
        choices=[(c, c) for c in Vote.VOTE_COUNT_FIELDS.keys()],
    )

    class Meta:
        model = Comment
        fields = ('action',)

    def create(self, validated_data):
        """Vote for the provided comment.
        """
        raise NotImplementedError(
            'VoteForCommentSerializer cannot create new resources.'
        )

    def update(self, instance, validated_data):
        """You cannot create objects with this class.
        """
        instance.vote(
            user=validated_data['user'],
            action=validated_data['action'],
        )
        return instance
