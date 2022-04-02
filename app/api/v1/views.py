# -*- coding: utf-8 -*-
from base64 import b64decode
from binascii import Error

from rest_framework import generics, views, status
from rest_framework.response import Response

from app.api.models import ApiToken
from app.authentication.models import Workspace

from app.api.v1.exceptions import ParameterValidationFailed, NotFound
from app.api.v1.pagination import CursorSetPagination
from app.api.v1.permissions import IsAuthenticated
from app.api.v1.throttling import ApiTokenThrottle


class BaseView(object):
    """Scope ViewSet requests to the provided Workspace.
    """
    throttle_classes = [ApiTokenThrottle]

    def dispatch(self, request, *args, **kwargs):
        """Set the request context before moving forward.
        """
        request.workspace = self.get_workspace(request)
        request.api_token = self.get_api_token(request, request.workspace)

        return super().dispatch(request, *args, **kwargs)

    def get_workspace(self, request):
        """Retrieve the Workspace from the headers.
        """
        workspace_id = request.META.get('HTTP_X_WORKSPACE_ID')

        if not workspace_id:
            return None

        return Workspace.objects.filter(id=workspace_id).first()

    def get_api_token(self, request, workspace):
        """Retrieve the ApiToken from the headers.
        """
        authorization = request.META.get('HTTP_AUTHORIZATION')

        if not authorization or not workspace:
            return None

        secret = ''.join(authorization.split()[1:])

        try:
            token_parts = b64decode(secret.encode()).decode().split(':')
        except Error:
            return None

        if len(token_parts) != 2:
            return None

        api_token = ApiToken.objects.filter(
            id=token_parts[0],
            workspace_id=workspace.id,
        ).first()

        if api_token and api_token.token == token_parts[1]:
            api_token.touch()
            return api_token


class DetailAPIView(BaseView, views.APIView):
    """Base API view for detail requests.
    """
    permission_classes = [IsAuthenticated]

    def format_response(self, data, *args, **kwargs):
        return Response(data, *args, **kwargs)

    def get(self, request, pk, format=None):
        instance = self.get_object(pk)
        serializer = self.serializer_class(instance)
        return self.format_response(serializer.data)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.format_response(serializer.data)
        return self.format_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListAPIView(BaseView, generics.ListAPIView):
    """Base API view for list requests.
    """
    pagination_class = CursorSetPagination
    permission_classes = [IsAuthenticated]


class FindAPIView(BaseView, views.APIView):
    """Base API view for find requests.
    """
    permission_classes = [IsAuthenticated]
    required_query_params = ['name']

    def parse_query_params(self, request):
        output = {}
        for query_param in self.required_query_params:
            value = request.query_params.get(query_param)
            if not value:
                raise ParameterValidationFailed()
            output[query_param] = value
        return output

    def get(self, request, *args, **kwargs):
        instance = self.find_object(
            query_params=self.parse_query_params(request),
            *args,
            **kwargs)
        if not instance:
            raise NotFound()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)
