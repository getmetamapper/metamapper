# -*- coding: utf-8 -*-
import rest_framework.serializers as serializers

import app.audit.decorators as audit
import app.definitions.models as models

import app.inspector.service as inspector
import app.revisioner.tasks.core as coretasks

import utils.fields as fields

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import ContentType
from django.db import transaction
from django.utils import timezone
from google.oauth2 import service_account
from guardian.models import UserObjectPermission, GroupObjectPermission

from app.authentication.models import User
from app.authorization.models import Group

from app.customfields.models import CustomField

from sshtunnel import BaseSSHTunnelForwarderError
from utils.mixins.serializers import MetamapperSerializer


def get_audit_kwargs(instance):
    """Make the parameters for logging audit activity.
    """
    content_type = ContentType.objects.get_for_model(instance)

    return {
        'target_object_id': instance.pk,
        'target_content_type_id': content_type.pk,
        'extras': {
            'datastore_id': instance.datastore_id,
        }
    }


class JdbcCredentialsSerializer(serializers.Serializer):
    """docstring for JdbcConnectionMixin
    """
    allowed_extra_fields = []

    engine = serializers.ChoiceField(choices=models.Datastore.ENGINE_CHOICES)
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)
    database = serializers.CharField(max_length=255)
    host = fields.HostnameField(max_length=512)
    port = fields.PortField()

    class Meta:
        model = models.Datastore

    def instance_attr(self, attrname):
        """Retrieve attribute from instance if exists.
        """
        return getattr(self.instance, attrname, None)

    def sanitize_extras(self, extras):
        """We expect some specific fields associated with this connection type:
        """
        output = {}

        for field in self.allowed_extra_fields:
            output[field] = extras.get(field, self.instance_attr(field))

        return output


class BigQueryConnectionSerializer(JdbcCredentialsSerializer):
    """Validates connectivity to BigQuery through service account info.
    """
    allowed_extra_fields = ['credentials']

    extras = serializers.JSONField(required=True)

    def validate_host(self, host):
        """Return a dummy host, since we do not need this field.
        """
        return 'bigquery.googleapis.com'

    def validate_username(self, username):
        """Return a dummy username, since we do not need this field.
        """
        return 'googleapis'

    def validate_password(self, password):
        """Return a dummy password, since we do not need this field.
        """
        return 'secret'

    def validate_port(self, port):
        """Return a dummy port, since we do not need this field.
        """
        return 443

    def validate_extras(self, extras):
        """We expect some specific fields associated with this connection type:
        {
            "credentials": {}
        }
        """
        extras = self.sanitize_extras(extras)

        try:
            service_account.Credentials.from_service_account_info(extras['credentials'] or {})
        except (AttributeError, ValueError, KeyError):
            raise serializers.ValidationError('Google service account information is an invalid format.')

        return extras


class AwsConnectionSerializer(JdbcCredentialsSerializer):
    """Validates connectivity to AWS Athena or Glue through IAM role and region.
    """
    allowed_extra_fields = ['role', 'region']

    extras = serializers.JSONField(required=True)

    def validate_host(self, host):
        """Return a dummy host, since we do not need this field.
        """
        return 'api.amazonaws.com'

    def validate_username(self, username):
        """Return a dummy username, since we do not need this field.
        """
        return 'amazonapis'

    def validate_password(self, password):
        """Return a dummy password, since we do not need this field.
        """
        return 'secret'

    def validate_port(self, port):
        """Return a dummy port, since we do not need this field.
        """
        return 443

    def validate_extras(self, extras):
        """We expect some specific fields associated with this connection type:
        {
            "region": "us-west-2",
            "role": "arn:aws:iam::123456789012:role/default"
        }
        """
        extras = self.sanitize_extras(extras)

        if not extras['role'] or not extras['region']:
            raise serializers.ValidationError('Amazon account information is an invalid format.')

        return extras


class HiveMetatastoreConnectionSerializer(JdbcCredentialsSerializer):
    """Validates connectivity to external Hive metastore hosted on Postgres, MS-SQL, or MySQL.
    """
    allowed_extra_fields = ['dialect']

    extras = serializers.JSONField(required=True)

    def validate_extras(self, extras):
        """We expect some specific fields associated with this connection type:
        {
            "dialect": "postgresql",
        }
        """
        extras = self.sanitize_extras(extras)

        if extras['dialect'] not in models.Datastore.SUPPORTED_HIVE_EXTERNAL_METASTORES:
            raise serializers.ValidationError(
                'Hive metastore must be one of: %s' % ', '.join(models.Datastore.SUPPORTED_HIVE_EXTERNAL_METASTORES)
            )

        return extras


class JdbcConnectionSerializer(MetamapperSerializer, JdbcCredentialsSerializer):
    """Validates connectivity to a database.
    """
    engine = serializers.ChoiceField(choices=models.Datastore.ENGINE_CHOICES)
    extras = serializers.JSONField(required=False, allow_null=True)

    ssh_host = serializers.IPAddressField(required=False, allow_null=True)
    ssh_user = fields.SysnameField(required=False, max_length=128, allow_null=True)
    ssh_port = fields.PortField(required=False, allow_null=True)
    ssh_enabled = serializers.BooleanField(required=False, default=False, allow_null=False)

    class Meta:
        model = models.Datastore

    def validate_extras(self, extras):
        return {} if extras is None else extras

    def validate_credentials(self, data):
        """Some datastores have non-standard credentials, so we should verify them via custom serializers.
        """
        engine = data.get('engine', self.instance_attr('engine'))

        validators = {
            models.Datastore.ATHENA: AwsConnectionSerializer,
            models.Datastore.BIGQUERY: BigQueryConnectionSerializer,
            models.Datastore.GLUE: AwsConnectionSerializer,
            models.Datastore.HIVE: HiveMetatastoreConnectionSerializer,
        }

        validator_class = validators.get(engine)

        if validator_class:
            validator = validator_class(self.instance, data=data, partial=self.partial)
            validator.is_valid(raise_exception=True)
            data.update(validator.validated_data)

        return data

    def validate_ssh(self, data):
        """SSH is optional unless one of the parameters is provided.
        """
        ssh_enabled = data.get('ssh_enabled', self.instance_attr('ssh_enabled'))
        if not ssh_enabled:
            return data
        for field in models.Datastore.REQUIRED_SSH_FIELDS:
            value = data.get(field, self.instance_attr(field))
            if not value:
                raise serializers.ValidationError({
                    'ssh': 'To enable SSH tunneling, please provide all required parameters.'
                })
        return data

    def validate_connection(self, datastore):
        """Check if the provided connection is valid.
        """
        is_verified = False

        try:
            is_verified = inspector.verify_connection(datastore)
        except BaseSSHTunnelForwarderError:
            raise serializers.ValidationError({
                'ssh_connection': 'Could not establish session to SSH gateway.'
            })

        if not is_verified:
            raise serializers.ValidationError({
                'jdbc_connection': 'Unable to connect to the datastore.',
            })

    def validate(self, data):
        """Run some validation checks against the payload as a whole.
        """
        data = self.validate_credentials(data)
        data = self.validate_ssh(data)

        workspace = self.context['request'].workspace
        datastore = models.Datastore(workspace=workspace, **data)

        self.validate_connection(datastore)

        return data

    def create(self, validated_data):
        raise NotImplementedError('JdbcConnectionSerializer cannot create new resources.')


class DatastoreSerializer(JdbcConnectionSerializer, serializers.ModelSerializer):
    """Enables user to create and update Datastore instances.
    """
    name = serializers.CharField(max_length=50, trim_whitespace=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=30, trim_whitespace=True),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    is_enabled = serializers.BooleanField(default=True)
    short_desc = serializers.CharField(
        max_length=140,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        required=False,
    )

    ssh_enabled = serializers.BooleanField(required=False, default=False, allow_null=True)

    class Meta:
        model = models.Datastore

        fields = (
            'name',
            'tags',
            'is_enabled',
            'short_desc',
            'engine',
            'username',
            'password',
            'database',
            'host',
            'port',
            'extras',
            'ssh_enabled',
            'ssh_host',
            'ssh_user',
            'ssh_port',)

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    def validate_ssh_enabled(self, ssh_enabled):
        """We should cast NULL values as false.
        """
        return bool(ssh_enabled)

    def validate_tags(self, tags):
        """We should remove any duplicate tags that exist.
        """
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def validate(self, data):
        """Run some validation checks against the payload as a whole.
        """
        data = self.validate_credentials(data)
        data = self.validate_ssh(data)
        return data

    @audit.capture_activity(
        verb='created',
        hydrater=get_audit_kwargs,
    )
    def create(self, validated_data):
        """Create a brand new Datastore instance.
        """
        creator = validated_data.pop('creator')
        with transaction.atomic():
            datastore = models.Datastore.objects.create(**validated_data)
            if datastore.pk:
                datastore.assign_all_perms(creator)
                run = datastore.run_history.create(
                    workspace_id=datastore.workspace_id,
                    started_at=timezone.now(),
                )
                coretasks.start_revisioner_run.apply_async(args=[run.id])
        return datastore

    @audit.capture_activity(
        verb='updated',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Update the provided Datastore instance.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)

        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        instance.database = validated_data.get('database', instance.database)
        instance.host = validated_data.get('host', instance.host)
        instance.port = validated_data.get('port', instance.port)
        instance.extras = validated_data.get('extras', instance.extras)

        instance.ssh_enabled = validated_data.get('ssh_enabled', instance.ssh_enabled)
        instance.ssh_host = validated_data.get('ssh_host', instance.ssh_host)
        instance.ssh_user = validated_data.get('ssh_user', instance.ssh_user)
        instance.ssh_port = validated_data.get('ssh_port', instance.ssh_port)

        if instance.connection_was_changed():
            self.validate_connection(instance)

        return instance


class ToggleDatastoreObjectPermissionsSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Toggles whether or not a serializer
    """
    object_permissions_enabled = serializers.BooleanField(default=False)

    class Meta:
        model = models.Datastore
        fields = ('object_permissions_enabled',)

    @audit.capture_activity(
        verb=lambda i: f"{'enabled' if i.object_permissions_enabled else 'disabled'} limited access to",
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Update the provided Table instance.
        """
        instance.object_permissions_enabled = validated_data.get(
            'object_permissions_enabled',
            instance.object_permissions_enabled,
        )

        return instance


class DatastoreAccessPrivilegesSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Update user permissions on a datastore
    """
    content_object = fields.RelatedObjectField(
        allowed_models=(User, Group),
        allow_null=False,
    )

    privileges = serializers.ListField(
        child=serializers.CharField(max_length=50, trim_whitespace=True),
        allow_empty=True,
        allow_null=False,
        required=True,
    )

    class Meta:
        model = models.Datastore
        fields = ('content_object', 'privileges',)

    def validate_content_object(self, content_object):
        """The content object must be part of the provided workspace.
        """
        if isinstance(content_object, (User,)) and not content_object.is_on_team(self.instance.workspace_id):
            raise serializers.ValidationError(
                'The provided user is not part of this workspace.',
                'invalid_user',
            )
        if isinstance(content_object, (Group,)) and content_object.workspace_id != self.instance.workspace_id:
            raise serializers.ValidationError(
                'The provided group is not part of this workspace.',
                'invalid_group',
            )
        return content_object

    def validate_privileges(self, privileges):
        """Ensure that the provided grant is valid.
        """
        allowed_permissions = models.Datastore.allowed_permissions()
        for privilege in privileges:
            if privilege not in allowed_permissions:
                raise serializers.ValidationError(
                    'Please provide valid privilege types.',
                    'invalid_grant',
                )
        return privileges

    def get_content_object_metadata(self):
        """Retrieve the correct content object meta items.
        """
        object_class = UserObjectPermission
        object_name = 'user'

        if isinstance(self.validated_data['content_object'], (Group,)):
            object_class = GroupObjectPermission
            object_name = 'group'

        return object_class, object_name

    def make_object_permission(self, permission, content_type):
        """Create unpersisted instances of the object permissions.
        """
        object_class, object_name = self.get_content_object_metadata()

        object_permission_kwargs = {
            object_name: self.validated_data['content_object'],
            'content_type': content_type,
            'object_pk': self.instance.pk,
            'permission': permission,
        }

        return object_class(**object_permission_kwargs)

    def commit_object_permissions(self, permissions, content_type):
        """Commit the object permissions for the User or Group to the metastore.
        """
        object_class, object_name = self.get_content_object_metadata()

        with transaction.atomic():
            filter_kwargs = {
                object_name: self.validated_data['content_object'],
                'content_type': content_type,
                'object_pk': self.instance.pk,
            }
            object_class.objects.filter(**filter_kwargs).delete()

            if permissions:
                object_class.objects.bulk_create(permissions)

        return self.instance

    @audit.capture_activity(
        verb='updated access privileges to',
        hydrater=get_audit_kwargs,
        capture_changes=False,
    )
    def save(self, *args, **kwargs):
        """Create the datastore access grants for the User or Group.
        """
        content_type = ContentType.objects.get_for_model(self.instance)

        object_permissions = []

        for permission in Permission.objects.filter(codename__in=self.validated_data.get('privileges', [])):
            object_permissions.append(
                self.make_object_permission(permission, content_type)
            )

        return self.commit_object_permissions(object_permissions, content_type)


class DisableCustomFieldsSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Update the disabled custom properties for the provided Datastore.
    """
    disabled_datastore_properties = serializers.ListField(
        child=serializers.CharField(max_length=20, trim_whitespace=True),
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    disabled_table_properties = serializers.ListField(
        child=serializers.CharField(max_length=20, trim_whitespace=True),
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = models.Datastore
        fields = ('disabled_datastore_properties', 'disabled_table_properties')

    def create(self, validated_data):
        raise NotImplementedError('DisableCustomFieldsSerializer cannot create Datastore instances.')

    def validate_disabled_datastore_properties(self, custom_field_ids):
        """Ensure that the custom fields actually exist.
        """
        custom_fields = CustomField.objects.filter(
            content_type__model='datastore',
            workspace_id=self.instance.workspace_id,
        ).values_list('id', flat=True)

        return [c for c in custom_field_ids if c in custom_fields]

    def validate_disabled_table_properties(self, custom_field_ids):
        """Ensure that the custom properties actually exist.
        """
        custom_fields = CustomField.objects.filter(
            content_type__model='table',
            workspace_id=self.instance.workspace_id,
        ).values_list('id', flat=True)

        return [c for c in custom_field_ids if c in custom_fields]

    @audit.capture_activity(
        verb='updated allowed properties',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Update the provided Table instance.
        """
        instance.disabled_datastore_properties = validated_data.get(
            'disabled_datastore_properties',
            instance.disabled_datastore_properties,
        )

        instance.disabled_table_properties = validated_data.get(
            'disabled_table_properties',
            instance.disabled_table_properties,
        )

        return instance


class TableSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Enables user to create and update Datastore instances.
    """
    tags = serializers.ListField(
        child=serializers.CharField(max_length=30),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    short_desc = serializers.CharField(max_length=140, allow_null=True, allow_blank=True, trim_whitespace=True)

    class Meta:
        model = models.Table
        fields = (
            'tags',
            'short_desc',)

    def validate_tags(self, tags):
        """We should remove any duplicate tags that exist.
        """
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    def create(self, validated_data):
        raise NotImplementedError('TableSerializer cannot create Table instances.')

    @audit.capture_activity(
        verb='updated',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Update the provided Table instance.
        """
        instance.tags = validated_data.get('tags', instance.tags)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        return instance


class ColumnSerializer(MetamapperSerializer, serializers.ModelSerializer):
    """Enables user to create and update Datastore instances.
    """
    short_desc = serializers.CharField(max_length=90, allow_null=True, allow_blank=True, trim_whitespace=True)

    class Meta:
        model = models.Column
        fields = ('short_desc',)

    def create(self, validated_data):
        raise NotImplementedError('ColumnSerializer cannot create Table instances.')

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    @audit.capture_activity(
        verb='updated',
        hydrater=get_audit_kwargs,
        capture_changes=True,
    )
    def update(self, instance, validated_data):
        """Update the provided Table instance.
        """
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        return instance


def get_asset_owner_audit_kwargs(instance):
    """Make the parameters for logging audit activity.
    """
    return {
        'target_object_id': instance.object_id,
        'target_content_type_id': instance.content_type_id,
        'action_object_object_id': instance.owner_id,
        'action_object_content_type_id': instance.owner_type_id,
        'extras': {
            'datastore_id': instance.content_object.datastore_id,
        }
    }


class AssetOwnerSerializer(MetamapperSerializer, serializers.Serializer):
    """Create and update an asset owner for a datastore object.
    """
    content_object = fields.RelatedObjectField(
        allowed_models=(models.Table,),
        allow_null=False,
    )

    owner = fields.RelatedObjectField(
        allowed_models=(User, Group,),
        allow_null=False,
    )

    order = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    class Meta:
        model = models.AssetOwner
        fields = ('content_object', 'owner', 'order',)

    def validate_owner(self, owner):
        """The owner must be part of the provided workspace.
        """
        workspace = self.context['request'].workspace
        has_error = False

        if isinstance(owner, (User,)) and not owner.is_on_team(workspace.id):
            has_error = True
        elif isinstance(owner, (Group,)) and not owner.workspace_id == workspace.id:
            has_error = True

        if has_error:
            raise serializers.ValidationError(
                'The provided owner is not part of this workspace.',
                'invalid',
            )
        return owner

    @audit.capture_activity(
        verb='added a new owner to',
        hydrater=get_asset_owner_audit_kwargs,
    )
    def create(self, validated_data):
        """Create a brand new Datastore instance.
        """
        position = validated_data.pop('order', None)
        instance = models.AssetOwner.objects.create(**validated_data)
        if position:
            instance.to(position)
        return instance

    def update(self, instance, validated_data):
        """Update the provided Table instance.
        """
        position = validated_data.pop('order', None)
        if position:
            instance.to(position)
        return instance
