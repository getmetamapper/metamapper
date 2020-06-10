# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.authorization.models as models
import app.authorization.emails as emails

from django.utils.translation import ugettext_lazy as _

from utils.mixins.serializers import MetamapperSerializer


class GrantMembershipSerializer(MetamapperSerializer, serializers.ModelSerializer):
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
