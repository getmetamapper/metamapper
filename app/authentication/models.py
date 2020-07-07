# -*- coding: utf-8 -*-
import datetime as dt
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from guardian.core import ObjectPermissionChecker

from app.authorization.models import Group, Membership
from app.sso.mixins import SSOTenantModel

from app.sso.providers.oauth2.google.client import GoogleClient
from app.sso.providers.oauth2.github.client import GithubClient

from utils.encrypt.fields import EncryptedCharField, EncryptedTextField
from utils.encrypt import rsa
from utils.managers import SearchManager
from utils.regexp import email_regex
from utils.mixins.models import (
    UUIDModel, TimestampedModel, AuditableModel
)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password.
        """
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Case-insensitive username search field.
        """
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser, TimestampedModel):
    """Authenticated user of the application.
    """
    username = None

    fname = models.CharField(max_length=100, null=False)
    lname = models.CharField(max_length=100, null=False)
    email = models.EmailField(db_index=True, unique=True, null=False)

    sso_access_token = EncryptedCharField(
        max_length=40,
        null=True,
        blank=False,
        default=uuid.uuid4,
        help_text="One-time token used for SSO flows",
    )
    sso_access_token_issued_at = models.DateTimeField(null=True, default=None)

    google_oauth2_token = EncryptedCharField(max_length=128, null=True, blank=False, default=None)
    google_oauth2_token_issued_at = models.DateTimeField(null=True, default=None)

    github_oauth2_token = EncryptedCharField(max_length=50, null=True, blank=False, default=None)
    github_oauth2_token_issued_at = models.DateTimeField(null=True, default=None)

    groups = models.ManyToManyField(Group)

    user_permissions = models.ManyToManyField(Permission)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['fname', 'lname', 'password']

    objects = UserManager()
    search_objects = SearchManager(fields=['fname', 'lname', 'email'])

    class Meta:
        db_table = 'auth_users'

    def __str__(self):
        return self.email

    @property
    def name(self):
        return '{0} {1}'.format(self.fname, self.lname)

    @property
    def is_superuser(self):
        return False

    def has_perm(self, perm, obj):
        """Check if the user has a permission scoped to an object.
        """
        checker = ObjectPermissionChecker(self)
        return checker.has_perm(perm, obj)

    def _google_client(self):
        if not self.google_oauth2_token:
            return None
        return GoogleClient(self.google_oauth2_token)

    def get_gsuite_domain(self):
        client = self._google_client()
        if client:
            return client.get_user_domain()

    def _github_client(self):
        if not self.github_oauth2_token:
            return None
        return GithubClient(self.github_oauth2_token)

    def get_github_organizations(self):
        client = self._github_client()
        if client:
            return client.get_organizations()

    def is_github_org_member(self, org_id):
        client = self._github_client()
        if client:
            return client.is_org_member(org_id)

    def set_github_oauth2_token(self, token):
        """Set the `github_oauth2_token` model field.
        """
        self.github_oauth2_token = token
        self.github_oauth2_token_issued_at = timezone.now()

    def set_google_oauth2_token(self, token):
        """Set the `google_oauth2_token` model field.
        """
        self.google_oauth2_token = token
        self.google_oauth2_token_issued_at = timezone.now()

    def set_sso_access_token(self, save=False):
        self.sso_access_token = uuid.uuid4()
        self.sso_access_token_issued_at = timezone.now()
        if save:
            self.save()

    def clear_sso_access_token(self, save=False):
        self.sso_access_token = None
        self.sso_access_token_issued_at = None
        if save:
            self.save()

    def is_sso_access_token_valid(self, token):
        """Check if access token is valid.
        """
        return self.sso_access_token == token and not self.sso_access_token_expired

    @property
    def sso_access_token_expired(self):
        return self.sso_access_token_issued_at is not None \
            and self.sso_access_token_issued_at < timezone.now() - dt.timedelta(seconds=(60 * 15))

    def change_password(self, password):
        """Changes user password and sends an alert email.
        """
        from app.authentication.emails import password_was_reset
        validate_password(password)
        self.set_password(password)
        self.save()
        password_was_reset(self.email)

    def check_email(self, email):
        return self.email.lower() == email.lower()

    def is_staff(self, workspace_id):
        return self.has_permissions(workspace_id, [Membership.MEMBER])

    def is_owner(self, workspace_id):
        return self.has_permissions(workspace_id, [Membership.OWNER])

    def is_on_team(self, workspace_id):
        return self.has_permissions(workspace_id, Membership.PERMISSION_GROUPS)

    def has_permissions(self, workspace_id, permissions):
        """Check if User has permissions (as list) for workspace.
        """
        filter_kwargs = {
            'workspace_id': workspace_id,
            'permissions__in': permissions
        }
        return self.memberships.filter(**filter_kwargs).exists()

    def permissions_for(self, workspace_id):
        """Retrieve the permission (as string) for the workspace.
        """
        try:
            return self.memberships.filter(
                workspace_id=workspace_id,
            ).values_list(
                'permissions', flat=True
            ).last()
        except ValidationError:
            return None


class Workspace(UUIDModel,
                SSOTenantModel,
                AuditableModel,
                TimestampedModel):
    """Represents a Tenant of the application.
    """
    slug = models.CharField(db_index=True, max_length=50, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)

    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    ssh_private_key = EncryptedTextField()
    ssh_public_key = models.TextField()

    team_members = models.ManyToManyField(
        to=User,
        through='authorization.Membership',
        through_fields=('workspace', 'user'),
        related_name='workspaces',
    )

    class Meta:
        db_table = 'auth_workspaces'

    objects = models.Manager()
    search_objects = SearchManager(fields=['name'])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.ssh_private_key and not self.ssh_public_key:
                self.set_ssh_keys()

            return super().save(*args, **kwargs)

    def set_ssh_keys(self, save=False):
        """Reset the ssh keys.
        """
        privkey, pubkey = rsa.generate_keypair()

        self.ssh_public_key = pubkey.decode()
        self.ssh_private_key = privkey.decode()

        if save:
            self.save()

    def grant_membership(self, user, permissions):
        """Grant permissions to a User for the Workspace. Performs UPSERT command.
        """
        email = user.email if isinstance(user, User) else user.lower()

        if permissions not in Membership.PERMISSION_GROUPS:
            raise ValidationError('The provided permission group is not valid.')

        if not email_regex.match(email):
            raise ValidationError('Enter a valid email address.')

        membership_existed = True
        membership = Membership.objects.filter(
            user_id=email,
            workspace=self,
            permissions=permissions,
        ).first()

        if membership:
            return membership, membership_existed

        self.revoke_membership(email)

        membership_existed = False
        membership = Membership.objects.create(
            user_id=email,
            workspace=self,
            permissions=permissions,
        )

        return membership, membership_existed

    def revoke_membership(self, user):
        """Remove a User from the Workspace via email address.
        """
        email = user.email if isinstance(user, User) else user.lower()

        membership = Membership.objects.filter(
            user_id=email,
            workspace=self,
        ).first()

        if membership:
            membership.delete()
