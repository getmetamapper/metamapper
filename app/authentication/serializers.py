# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.authentication.models as models

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.core.validators import validate_slug
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from utils.mixins.serializers import MetamapperSerializer


class UserSerializer(MetamapperSerializer, serializers.ModelSerializer):
    fname = serializers.CharField(required=True, max_length=60)
    lname = serializers.CharField(required=True, max_length=60)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = models.User
        fields = (
            'fname',
            'lname',
            'email',
            'password',
            'created_at',
            'updated_at')
        write_only_fields = ('password',)

    def validate_password(self, password):
        try:
            validate_password(password, user=models.User)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages[0], 'too_weak')
        return password

    def validate_email(self, email):
        user = models.User.objects.filter(email__iexact=email).first()
        if user:
            raise serializers.ValidationError('User with this email already exists.', 'exists')
        return email

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class CurrentUserSerializer(MetamapperSerializer, serializers.ModelSerializer):
    fname = serializers.CharField(required=True, max_length=60)
    lname = serializers.CharField(required=True, max_length=60)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    current_password = serializers.CharField(style={'input_type': 'password'}, required=False)

    default_error_messages = {
        'wrong_password': _('The password you provided is incorrect.'),
    }

    class Meta:
        model = models.User
        fields = (
            'fname',
            'lname',
            'email',
            'current_password',
            'password')
        write_only_fields = ('current_password', 'password',)

    def validate_current_password(self, password):
        user = self.context['request'].user
        if user.check_password(password):
            return password
        else:
            self.fail('wrong_password')

    def validate_password(self, password):
        user = self.context['request'].user
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(e.messages[0], 'too_weak')
        return password

    def validate_email(self, email):
        user = self.context['request'].user

        if user.email.lower() == email.lower():
            return email

        if models.User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('User with this email already exists.', 'exists')

        return email

    def create(self, validated_data):
        raise NotImplementedError('CurrentUserSerializer cannot create new users.')

    def update(self, instance, validated_data):
        password = validated_data.get('password')

        # Only update the password if it has changed.
        if password and not instance.check_password(password):
            instance.set_password(password)

        email = validated_data.get('email', instance.email).lower()

        with transaction.atomic():
            instance.memberships.update(user_id=email)
            instance.email = email
            instance.fname = validated_data.get('fname', instance.fname)
            instance.lname = validated_data.get('lname', instance.lname)
            instance.save()
        return instance


class WorkspaceSerializer(MetamapperSerializer, serializers.ModelSerializer):
    name = serializers.CharField(required=True, min_length=3, max_length=255)
    slug = serializers.CharField(required=True, min_length=3, max_length=50)

    class Meta:
        model = models.Workspace
        fields = (
            'id',
            'name',
            'slug',
            'creator_id',
            'created_at',
            'updated_at')

    def slug_is_unique(self, slug):
        workspace_exists = models.Workspace.objects.filter(slug__iexact=slug.lower()).exists()
        if workspace_exists:
            raise serializers.ValidationError({'slug': 'Slug already exists.'}, 'exists')
        return slug

    def slug_is_valid(self, slug):
        if slug:
            try:
                validate_slug(slug)
            except django_exceptions.ValidationError:
                raise serializers.ValidationError({'slug': 'Slug is an invalid format.'}, 'invalid')
        return slug

    def validate(self, data):
        """Validate the workspace payload.
        """
        slug = self.slug_is_valid(data.get('slug'))
        if slug:
            if not self.instance or self.instance.slug != slug:
                self.slug_is_unique(slug)
        return data

    def create(self, validated_data):
        workspace = None
        with transaction.atomic():
            workspace = models.Workspace.objects.create(**validated_data)
            workspace.grant_membership(workspace.creator, models.Membership.OWNER)
        return workspace

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance
