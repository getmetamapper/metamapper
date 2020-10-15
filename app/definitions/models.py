# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import ContentType, GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

from guardian.shortcuts import assign_perm
from ordered_model.models import OrderedModel

from app.authentication.models import Workspace
from app.comments.models import Comment
from app.customfields.models import CustomPropertiesModel
from app.revisioner.mixins import RevisableModel

from utils.delete.models import SoftDeletionModel
from utils.encrypt.fields import EncryptedCharField
from utils.managers import SearchManager
from utils.mixins.models import (
    StringPrimaryKeyModel, TimestampedModel, AuditableModel
)
from utils.postgres.managers import PostgresManager
from utils.shortcuts import generate_unique_slug


def make_audit_kwargs(instance):
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


class AssetOwner(OrderedModel, TimestampedModel):
    """Represents an owner of a data asset.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    object_id = models.IntegerField()
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
    )

    content_object = GenericForeignKey('content_type', 'object_id')

    owner_id = models.IntegerField()
    owner_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+',
    )
    owner = GenericForeignKey('owner_type', 'owner_id')

    order_with_respect_to = ('object_id', 'content_type')

    class Meta:
        unique_together = ('workspace', 'object_id', 'content_type', 'owner_id', 'owner_type')


class Datastore(StringPrimaryKeyModel,
                SoftDeletionModel,
                AuditableModel,
                CustomPropertiesModel,
                TimestampedModel):
    """Represents a JDBC connectable datastore.
    """
    POSTGRESQL = 'postgresql'
    SQLSERVER = 'sqlserver'
    MYSQL = 'mysql'
    REDSHIFT = 'redshift'
    SNOWFLAKE = 'snowflake'
    ORACLE = 'oracle'
    BIGQUERY = 'bigquery'
    ATHENA = 'athena'
    GLUE = 'glue'
    HIVE = 'hive'
    AZURE_SQL = 'azure_sql'
    AZURE_DWH = 'azure_dwh'

    ENGINE_CHOICES = (
        (POSTGRESQL, 'PostgreSQL'),
        (SQLSERVER, 'SQL Server'),
        (MYSQL, 'MySQL'),
        (REDSHIFT, 'Redshift'),
        (SNOWFLAKE, 'Snowflake'),
        (ORACLE, 'Oracle'),
        (BIGQUERY, 'Google BigQuery'),
        (ATHENA, 'AWS Athena'),
        (GLUE, 'AWS Glue'),
        (AZURE_SQL, 'Azure SQL Database'),
        (AZURE_DWH, 'Azure Synapse'),
        (HIVE, 'Hive Metastore'),
    )

    SUPPORTED_HIVE_EXTERNAL_METASTORES = [
        MYSQL,
        POSTGRESQL,
        SQLSERVER,
    ]

    REQUIRED_SSH_FIELDS = [
        'ssh_host',
        'ssh_user',
        'ssh_port',
    ]

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='datastores',
    )

    audited_fields = [
        'name',
        'short_desc',
        'tags',
        'is_enabled',
        'custom_properties',
        'host',
        'username',
        'password',
        'database',
        'port',
        'ssh_enabled',
        'ssh_host',
        'ssh_port',
        'ssh_user',
    ]

    name = models.CharField(max_length=255, null=False, blank=False)
    slug = models.CharField(max_length=300, null=False, blank=False)
    tags = ArrayField(models.CharField(max_length=32, blank=True), default=list)
    is_enabled = models.BooleanField(default=True)
    version = models.CharField(max_length=255, null=True, blank=False)

    engine = models.CharField(max_length=16, choices=ENGINE_CHOICES, null=False, blank=False)
    host = models.CharField(max_length=255, null=False, blank=False)
    username = models.CharField(max_length=128, null=False, blank=False)
    password = EncryptedCharField(max_length=128, null=False, blank=False)
    database = models.CharField(max_length=128, null=False, blank=False)
    port = models.PositiveIntegerField(null=False, blank=False, validators=[MaxValueValidator(65535)])
    extras = JSONField(default=dict)

    ssh_enabled = models.BooleanField(default=False)
    ssh_host = models.CharField(max_length=128, null=True, blank=False)
    ssh_port = models.PositiveIntegerField(null=True, blank=False, validators=[MaxValueValidator(65535)])
    ssh_user = models.CharField(max_length=128, null=True, blank=False)

    short_desc = models.CharField(max_length=140, null=True, blank=True)

    # List of custom fields that should be disabled for this datastore.
    disabled_datastore_properties = ArrayField(models.CharField(max_length=20), default=list)

    # List of custom fields that should be disabled for all tables within this datastore.
    disabled_table_properties = ArrayField(models.CharField(max_length=20), default=list)

    # If set to false, anyone within your workspace can access the datastore
    # and its objects. Permissions default to the workspace level.
    object_permissions_enabled = models.BooleanField(default=True)

    search_objects = SearchManager(fields=['name', 'engine', 'tags'])

    class Meta:
        unique_together = ('workspace', 'name',)

        # Permissions for datastores and its children objects. This is ignored
        # for any users with OWNER status.
        permissions = (
            ('change_datastore_metadata', 'Change datastore metadata'),
            ('change_datastore_settings', 'Change datastore settings'),
            ('change_datastore_connection', 'Change datastore connection'),
            ('change_datastore_access', 'Change datastore access'),
            ('comment_on_datastore', 'Comment on datastore'),
        )

    def __init__(self, *args, **kwargs):
        super(Datastore, self).__init__(*args, **kwargs)
        self.__slug = self.slug

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        """Override `save` method to set the `slug` attribute.
        """
        if not self.slug or self.__slug != self.slug:
            self.slug = generate_unique_slug(
                self.__class__,
                self.name,
            )
        return super().save(*args, **kwargs)

    @classmethod
    def allowed_permissions(cls):
        """All of the available permission grants in the database.
        """
        return [
            '%s_datastore' % p for p in cls._meta.default_permissions
        ] + [p[0] for p in cls._meta.permissions]

    @property
    def datastore_id(self):
        """Alias for the `pk` for audit reasons.
        """
        return self.pk

    @property
    def parent_resource(self):
        """Alias for the `parent` for audit reasons.
        """
        return None

    @property
    def revisioner_label(self):
        """Decorator function for label in Revisioner output.
        """
        return self.name

    @property
    def display_name(self):
        """The displayable name of the object.
        """
        return self.name

    @property
    def most_recent_run(self):
        """Get the most recent Revisioner run.
        """
        return self.run_history.order_by('-created_at').first()

    @property
    def last_committed_run(self):
        """Get the most recent Revisioner completed run.
        """
        return (
            self.run_history
                .filter(finished_at__isnull=False)
                .order_by('-created_at')
                .first()
        )

    @property
    def has_completed_run(self):
        """Check if the datastore has a completed run.
        """
        return self.run_history.filter(finished_at__isnull=False).count() > 0

    @property
    def disabled_custom_fields(self):
        return self.disabled_datastore_properties

    def connection_was_changed(self):
        """Check if the JDBC connection was updated.
        """
        jdbc_fields = [
            'host',
            'username',
            'password',
            'port',
            'database',
        ]
        return self.is_dirty(*jdbc_fields)

    def assign_perm(self, user_or_group, perm):
        """Assign a set of permissions to a User or Group.
        """
        return assign_perm(perm, user_or_group, self)

    def assign_all_perms(self, user_or_group):
        """Assign every permission to a User or Group.
        """
        with transaction.atomic():
            for perm in Datastore.allowed_permissions():
                self.assign_perm(user_or_group, perm)


class Schema(AuditableModel,
             RevisableModel,
             SoftDeletionModel,
             TimestampedModel):
    """Represents a schema within a datastore.
    """
    audited_fields = [
        'tags',
    ]

    object_id = models.CharField(db_index=True, max_length=256, null=True, default=None)

    datastore = models.ForeignKey(
        to=Datastore,
        on_delete=models.CASCADE,
        related_name='schemas',
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    name = models.CharField(db_index=True, max_length=256, null=False, blank=False)
    tags = ArrayField(models.CharField(max_length=32, blank=True), default=list)

    search_objects = SearchManager(fields=['name'])

    @property
    def parent_resource(self):
        return self.datastore

    @property
    def display_name(self):
        """The displayable name of the object.
        """
        return self.name

    class Meta:
        unique_together = ('datastore', 'name',)

    def __str__(self):
        return self.name


class Table(AuditableModel,
            CustomPropertiesModel,
            RevisableModel,
            SoftDeletionModel,
            TimestampedModel):
    """Represents a table within a schema.
    """
    audited_fields = [
        'custom_properties',
        'short_desc',
        'tags',
    ]

    comments = GenericRelation(Comment, related_query_name="table")

    owners = GenericRelation(AssetOwner, related_query_name="table")

    object_id = models.CharField(db_index=True, max_length=256, null=True, default=None)

    schema = models.ForeignKey(
        to=Schema,
        on_delete=models.CASCADE,
        related_name='tables',
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    name = models.CharField(db_index=True, max_length=256, null=False, blank=False)
    tags = ArrayField(models.CharField(max_length=32, blank=True), default=list)
    kind = models.CharField(max_length=100, null=False, blank=False)

    db_comment = models.TextField(null=True, blank=True)
    short_desc = models.TextField(null=True, blank=True)
    properties = JSONField(default=dict)

    search_objects = SearchManager(fields=['name', 'schema__name', 'short_desc'])

    class Meta:
        unique_together = ('schema', 'name',)

    def to_doc(self):
        return {
            'pk': str(self.id),
            'workspace_id': self.workspace.id,
            'datastore_id': self.schema.datastore.id,
            'datastore': self.schema.datastore.name,
            'schema': self.schema.name,
            'name': self.name,
            'description': self.short_desc,
        }

    @property
    def parent_resource(self):
        return self.schema

    @property
    def display_name(self):
        """The displayable name of the object.
        """
        return self.name

    @property
    def disabled_custom_fields(self):
        return self.schema.datastore.disabled_table_properties

    @property
    def datastore(self):
        return self.schema.datastore

    @property
    def datastore_id(self):
        return self.schema.datastore_id

    @property
    def datastore_slug(self):
        return self.schema.datastore.slug

    @property
    def search_label(self):
        return '%s.%s' % (self.schema.name, self.name)

    @property
    def search_pathname(self):
        return '/datastores/%s/definition/%s/%s/overview' % (
            self.datastore_slug,
            self.schema.name,
            self.name,
        )

    def as_search_result(self):
        return {
            'pathname': self.search_pathname,
            'label': self.search_label,
            'description': self.short_desc,
            'datastore_id': self.datastore_id,
        }

    @property
    def revisioner_pathname(self):
        return '/datastores/%s/assets?schema=%s' % (
            self.datastore_slug,
            self.schema.name,
        )

    @property
    def revisioner_parent_label(self):
        """Decorator function for label in Revisioner output.
        """
        return self.schema.name


class TableProperty(models.Model):
    id = models.BigIntegerField(primary_key=True)
    table = models.ForeignKey(Table, related_name='table_properties', on_delete=models.DO_NOTHING)
    value = models.TextField(db_column='property_value')

    class Meta:
        managed = False
        db_table = 'definitions_table_properties'


class Column(AuditableModel,
             TimestampedModel,
             SoftDeletionModel,
             RevisableModel):
    """Represents a column within a table.
    """
    audited_fields = [
        'short_desc',
        'tags',
    ]

    comments = GenericRelation(Comment, related_query_name="column")

    object_id = models.CharField(db_index=True, max_length=256, null=True, default=None)

    table = models.ForeignKey(
        to=Table,
        on_delete=models.CASCADE,
        related_name='columns',
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    name = models.CharField(db_index=True, max_length=256, null=False, blank=False)
    ordinal_position = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1)])
    data_type = models.CharField(max_length=255, null=False, blank=False)
    max_length = models.IntegerField(null=True)
    numeric_scale = models.IntegerField(null=True)
    is_primary = models.BooleanField(null=False, default=False)
    is_nullable = models.BooleanField(null=False)
    default_value = models.CharField(max_length=255, null=True, blank=True)
    db_comment = models.TextField(null=True, blank=True)
    short_desc = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('table', 'name',)

    @property
    def parent_resource(self):
        return self.table

    @property
    def display_name(self):
        """The displayable name of the object.
        """
        return self.name

    @property
    def datastore_id(self):
        return self.table.datastore_id

    @property
    def datastore(self):
        return self.table.datastore

    @property
    def datastore_slug(self):
        return self.table.datastore_slug

    @property
    def search_label(self):
        return '%s.%s.%s' % (self.table.schema.name, self.table.name, self.name)

    @property
    def search_pathname(self):
        return '/datastores/%s/definition/%s/%s/columns' % (
            self.datastore_slug,
            self.table.schema.name,
            self.table.name,
        )

    def as_search_result(self):
        return {
            'pathname': self.search_pathname,
            'label': self.search_label,
            'description': self.short_desc,
            'datastore_id': self.datastore_id,
        }

    def to_doc(self):
        return {
            'pk': str(self.id),
            'workspace_id': self.table.workspace.id,
            'datastore_id': self.table.schema.datastore.id,
            'datastore': self.table.schema.datastore.name,
            'schema': self.table.schema.name,
            'table': self.table.name,
            'name': self.name,
            'description': self.short_desc,
        }

    @property
    def full_data_type(self):
        dtype = self.data_type
        if self.max_length:
            dtype = '{0}({1}'.format(dtype, self.max_length)
            if self.numeric_scale:
                dtype = '{0}, {1}'.format(dtype, self.numeric_scale)
            dtype = dtype + ')'
        return dtype

    @property
    def revisioner_pathname(self):
        return '/datastores/%s/definition/%s/%s/columns' % (
            self.datastore_slug,
            self.table.schema.name,
            self.table.name,
        )

    @property
    def revisioner_parent_label(self):
        """Decorator function for label in Revisioner output.
        """
        return '%s.%s' % (self.table.schema.name, self.table.name)


class Index(RevisableModel, TimestampedModel):
    """Represents a index within a table.
    """
    object_id = models.CharField(db_index=True, max_length=256, null=True, default=None)

    table = models.ForeignKey(
        to=Table,
        on_delete=models.CASCADE,
        related_name='indexes',
    )

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    name = models.CharField(db_index=True, max_length=512)
    kind = models.CharField(max_length=50)

    is_primary = models.BooleanField(null=False, default=False)
    is_unique = models.BooleanField(null=False, default=False)

    sql = models.TextField(null=True)

    columns = models.ManyToManyField(Column, through=u'IndexColumn')

    objects = PostgresManager()

    @property
    def display_name(self):
        """The displayable name of the object.
        """
        return self.name

    @property
    def parent_resource(self):
        return self.table

    @property
    def datastore_id(self):
        return self.table.datastore_id

    @property
    def datastore_slug(self):
        return self.table.datastore_slug

    @property
    def revisioner_pathname(self):
        return '/datastores/%s/definition/%s/%s/indexes' % (
            self.datastore_slug,
            self.table.schema.name,
            self.table.name,
        )

    @property
    def revisioner_parent_label(self):
        """Decorator function for label in Revisioner output.
        """
        return '%s.%s' % (self.table.schema.name, self.table.name)

    class Meta:
        unique_together = ('table', 'name',)


class IndexColumn(TimestampedModel):
    """Relationship between an index and multiple existing columns.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='+',
    )

    index = models.ForeignKey(
        to=Index,
        on_delete=models.CASCADE,
        related_name='index_columns',
    )

    column = models.ForeignKey(to=Column, on_delete=models.CASCADE)

    ordinal_position = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(1)])

    objects = PostgresManager()

    class Meta:
        unique_together = ('index', 'column', 'workspace',)
