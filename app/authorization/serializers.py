# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.authorization.models as models
import app.authorization.emails as emails

from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from app.authentication.models import User
from utils.mixins.serializers import MetamapperSerializer


class GrantMembershipSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Adds or updates a User membership to a Workspace.
    """
    email = serializers.EmailField(required=True)
    permissions = serializers.ChoiceField(
        choices=models.Membership.PERMISSION_GROUP_CHOICES,
        error_messages={'invalid_choice': _('The provided permission group is not valid.')},
    )

    class Meta:
        model = models.Membership
        fields = ('email', 'permissions',)

    def validate_email(self, email):
        user = self.context['request'].user
        if email == user.email:
            raise serializers.ValidationError('You cannot alter your own membership.', 'self_update')
        return email

    def save(self, workspace):
        """Create or update the membership to the workspace.
        """
        membership, membership_existed = workspace.grant_membership(
            user=self.validated_data['email'],
            permissions=self.validated_data['permissions'],
        )

        if membership and not membership_existed:
            emails.membership_granted(
                self.validated_data['email'],
                workspace,
                self.validated_data['permissions'],
            )

        return membership


class RevokeMembershipSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Removes a User from a Workspace.
    """
    email = serializers.EmailField(required=True)

    class Meta:
        model = models.Membership
        fields = ('email',)

    def validate_email(self, email):
        if not self.instance.is_owner:
            return email
        workspace = self.context['request'].workspace
        owners_count = workspace.memberships.filter(permissions=models.Membership.OWNER).count()
        if owners_count <= 1:
            raise serializers.ValidationError(
                'You cannot leave this workspace as you are the only owner.',
                'only_owner',
            )
        return email

    def save(self, workspace):
        """Revoke the membership from the workspace.
        """
        if self.instance.delete():
            emails.membership_revoked(self.instance.user_id, workspace)


class GroupSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Used to perform CRUD actions on the native Django Group model.
    """
    name = serializers.CharField(
        required=True,
        max_length=25,
        trim_whitespace=True,
        allow_null=False,
        allow_blank=False,
    )

    description = serializers.CharField(
        required=False,
        max_length=60,
        trim_whitespace=True,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = models.Group
        fields = ('name', 'description',)

    def create(self, validated_data):
        """Create a brand new Datastore instance.
        """
        with transaction.atomic():
            group = models.Group.objects.create(**validated_data)
        return group

    def update(self, instance, validated_data):
        """Update the provided CustomField instance.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class AddUserToGroupSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Used to add a team member to the group.
    """
    user = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects)

    class Meta:
        model = User
        fields = ('user',)

    def validate_user(self, user):
        """The user must be part of the provided workspace.
        """
        if not user.is_on_team(self.instance.workspace_id):
            raise serializers.ValidationError(
                'The provided user is not part of this workspace.',
                'no_membership',
            )
        return user

    def save(self, *args, **kwargs):
        """Grant the membership to the Group.
        """
        self.instance.user_set.add(self.validated_data['user'])
        return self.validated_data['user']


class RemoveUserFromGroupSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Used to remove a team member from the group.
    """
    user = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects)

    class Meta:
        model = User
        fields = ('user',)

    def save(self, *args, **kwargs):
        """Revoke the membership from the Group.
        """
        self.instance.user_set.remove(self.validated_data['user'])
        return self.validated_data['user']
