# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError

from django.utils.crypto import get_random_string
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from app.authentication.models import User, Workspace
from app.authorization.models import Membership


def get_current_workspace(request):
    """Retrieve the current workspace based on the provider header value.
    """
    workspace = None
    pk = request.META.get('HTTP_X_WORKSPACE_ID')
    if pk:
        try:
            workspace = Workspace.objects.get(pk=pk)
        except (Workspace.DoesNotExist, ValidationError):
            pass
    return workspace


class CurrentWorkspaceMiddleware(object):
    def resolve(self, next, root, info, **args):
        """Attach the current workspace to the request.
        """
        if not hasattr(info.context, 'workspace') or info.context.workspace is None:
            info.context.workspace = get_current_workspace(info.context)
        return next(root, info, **args)


def get_anonymous_user(request):
    """Retrieve or create the anonymous user used by the AnonymousAuthenticationMiddleware class.
    """
    email = 'anonymous@metamapper.io'

    if not hasattr(request, '_cached_user'):
        try:
            request._cached_user = User.objects.get(email=email)
        except User.DoesNotExist:
            request._cached_user = User.objects.create_user(
                email=email,
                fname='Anonymous',
                lname='User',
                password=get_random_string(40),
            )

    workspace, _ = Workspace.objects.get_or_create(
        slug='default',
        defaults={
            'name': 'default',
            'creator': request._cached_user,
        },
    )

    if not request._cached_user.is_on_team(workspace.id):
        workspace.grant_membership(request._cached_user, Membership.OWNER)

    return request._cached_user


class AnonymousAuthenticationMiddleware(MiddlewareMixin):
    """This middleware can be used if you do not want authentication on top of
    your Metamapper instance. We do NOT recommend using this in production unless
    you are positive you do not want the concept of authentication and users.
    """
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'app.authentication.middleware.AnonymousAuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_anonymous_user(request))
