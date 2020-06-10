# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay
import graphql_jwt
import graphql_jwt.shortcuts as jwt

import app.authentication.emails as emails
import app.authentication.models as models
import app.authentication.schema as schema
import app.authentication.serializers as serializers

import utils.mixins.mutations as mixins
import utils.shortcuts as shortcuts

from django.core import exceptions
from django.contrib.auth.tokens import default_token_generator

from utils.errors import PasswordResetTokenExpired
from utils.graphql.types import ErrorType

from app.authorization.permissions import (
    AllowAny,
    AllowAuthenticated,
    WorkspaceOwnersOnly,
)


class Register(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Mutation to register a user.
    """
    permission_classes = (AllowAny,)

    class Meta:
        serializer_class = serializers.UserSerializer

    class Input:
        fname = graphene.String(required=True)
        lname = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(schema.UserType)
    jwt = graphene.Field(graphene.String)

    @classmethod
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            cls.model_name: instance,
            'errors': errors,
        }
        if instance and instance.pk is not None:
            return_kwargs['jwt'] = jwt.get_token(instance)
        return cls(**return_kwargs)


class ResetPassword(graphene.Mutation):
    """Mutation for requesting a password reset email.
    """
    class Input:
        email = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(ErrorType)

    def mutate(self, info, email):
        user = shortcuts.get_object_or_404(models.User, email=email)
        token = default_token_generator.make_token(user)
        emails.reset_password(user.email, user.id, token)
        return ResetPassword(ok=True, errors=None)


class ResetPasswordConfirm(graphene.Mutation):
    """Mutation for changing the user password.
    """
    class Input:
        uid = graphene.Int(required=True)
        token = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(ErrorType)

    @classmethod
    def perform_mutation(cls, user, token, password):
        if not default_token_generator.check_token(user, token):
            raise PasswordResetTokenExpired('Password reset token is no longer valid.')
        user.change_password(password)
        return user

    def mutate(self, info, uid, token, password):
        errors = None
        user = shortcuts.get_object_or_404(models.User, pk=uid)
        try:
            ResetPasswordConfirm.perform_mutation(user, token, password)
        except PasswordResetTokenExpired:
            errors = [
                ErrorType(resource='User', field='password_reset_token', code='invalid')
            ]
        except exceptions.ValidationError:
            errors = [
                ErrorType(resource='User', field='password', code='invalid')
            ]
        return ResetPasswordConfirm(ok=(errors is None), errors=errors)


class LoginWithSSOToken(graphene.Mutation):
    """Mutation for logging in with a one-time SSO token.
    """
    class Input:
        uid = graphene.Int(required=True)
        token = graphene.String(required=True)

    jwt = graphene.String()

    def mutate(self, info, uid, token):
        """Return a JWT if the access token is valid.
        """
        jwt_token = None
        user = models.User.objects.filter(id=uid).first()
        if user:
            if user.is_sso_access_token_valid(token):
                jwt_token = jwt.get_token(user)
            user.clear_sso_access_token(True)
        return LoginWithSSOToken(jwt=jwt_token)


class UpdateCurrentUser(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Mutation to update metadata about the current user.
    """
    permission_classes = (AllowAuthenticated,)

    class Meta:
        serializer_class = serializers.CurrentUserSerializer

    class Input:
        current_password = graphene.String(required=False)
        fname = graphene.String(required=False)
        lname = graphene.String(required=False)
        email = graphene.String(required=False)
        password = graphene.String(required=False)

    user = graphene.Field(schema.UserType)
    jwt = graphene.Field(graphene.String)

    @classmethod
    def get_serializer_kwargs(cls, root, info, **data):
        return {
            'instance': info.context.user,
            'data': {k: v for k, v in data.items() if v},
            'partial': True,
            'context': {
                'request': info.context,
            },
        }

    @classmethod
    def prepare_response(cls, instance, errors):
        return_kwargs = {
            cls.model_name: instance,
            'jwt': jwt.get_token(instance),
            'errors': errors,
        }
        return cls(**return_kwargs)


class CreateWorkspace(mixins.CreateMutationMixin, relay.ClientIDMutation):
    """Mutation for creating a new workspace.
    """
    permission_classes = (AllowAuthenticated,)

    class Meta:
        serializer_class = serializers.WorkspaceSerializer

    class Input:
        name = graphene.String(required=True)
        slug = graphene.String(required=True)

    workspace = graphene.Field(schema.WorkspaceType)

    @classmethod
    def perform_save(cls, serializer, info):
        return serializer.save(creator=info.context.user)


class UpdateWorkspace(mixins.UpdateMutationMixin, relay.ClientIDMutation):
    """Mutation for updating an existing workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.WorkspaceSerializer

    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        slug = graphene.String(required=False)

    workspace = graphene.Field(schema.WorkspaceType)


class DeleteWorkspace(mixins.DeleteMutationMixin, relay.ClientIDMutation):
    """Permanently remove an existing workspace.
    """
    permission_classes = (WorkspaceOwnersOnly,)

    class Meta:
        serializer_class = serializers.WorkspaceSerializer


class Mutation(graphene.ObjectType):
    # JWT Authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    login_with_sso_token = LoginWithSSOToken.Field(name='loginWithSSOToken')

    # Current User Management
    register_user = Register.Field()
    update_current_user = UpdateCurrentUser.Field()
    reset_password = ResetPassword.Field()
    reset_password_confirm = ResetPasswordConfirm.Field()

    # Workspace Management
    create_workspace = CreateWorkspace.Field()
    update_workspace = UpdateWorkspace.Field()
    delete_workspace = DeleteWorkspace.Field()
