# -*- coding: utf-8 -*-
import json
import os
import six

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.generic import View

from graphql import GraphQLError
from graphene_django.views import GraphQLView

from app.authentication.models import Workspace

from utils.errors import format_error as format_graphql_error
from utils.encrypt.fields import EncryptedField
from utils.logging import Logger
from utils.uploads import place_files_in_operations

from metamapper.loaders import GlobalDataLoader


def get_content_types():
    """If we reset the database, `django_content_types` does not
    exist. So we have to prevent Django from loading the ContentType
    model and throwing an error.
    """
    if settings.DB_RESET:
        return []
    return ContentType.objects.all()


def sanitize_variables(variables):
    """Prevents sensitive values from being exposed in the logs.
    """
    variables = variables or {}
    output = {}
    for k, v in variables.items():
        value = v
        if k in ENCRYPTED_FIELDS:
            value = '***********'
        output[k] = value
    return output


JWT_RELATED_ERRORS = (
    'Signature has expired',
    'Error decoding signature',
)

ENCRYPTED_FIELDS = list({
    f.name
    for c in get_content_types()
    for f in c.model_class()._meta.fields if isinstance(f, EncryptedField)
})


logger = Logger('metamapper.graphql')


class MetamapperGraphQLView(GraphQLView):
    """Modified GraphQLView to inject workspace object into context.
    """
    def dispatch(self, request, *args, **kwargs):
        """Attach workspace to request object if available.
        """
        request.workspace = None
        pk = request.META.get('HTTP_X_WORKSPACE_ID')
        if pk:
            try:
                request.workspace = Workspace.objects.get(pk=pk)
            except (Workspace.DoesNotExist, ValidationError):
                pass
        return super(MetamapperGraphQLView, self).dispatch(request, *args, **kwargs)

    def get_context(self, request):
        """Attach the global DataLoader class to the request.
        """
        request = self.request
        request.loaders = GlobalDataLoader(request)
        return request

    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)
        return {'message': six.text_type(error)}

    def parse_body(self, request):
        """Update method to handle multipart request spec for "multipart/form-data" body.
        """
        content_type = self.get_content_type(request)
        if content_type == 'multipart/form-data':
            operations = json.loads(request.POST.get('operations', '{}'))
            files_map = json.loads(request.POST.get('map', '{}'))
            return place_files_in_operations(
                operations,
                files_map,
                request.FILES
            )
        return super().parse_body(request)

    def log_operation(self, request, status_code, operation_name, variables):
        """Log the HTTP request.
        """
        log_kwargs = {
            'operation': operation_name,
            'user': request.user.pk if request.user else None,
            'vars': sanitize_variables(variables),
        }

        orderby = ['operation', 'user', 'vars']
        message = []

        for key in orderby:
            if not log_kwargs[key]:
                continue
            message.append(
                '({key}: {value})'.format(key=key, value=log_kwargs[key])
            )

        logger.info(' '.join(message))

    def get_response(self, request, data, show_graphiql=False):
        """Handler for GraphQL response.
        """
        query, variables, operation_name, id = self.get_graphql_params(request, data)

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

        result = None
        status_code = 200

        if execution_result:
            response = {}

            if execution_result.errors:
                response['errors'] = []

                for e in execution_result.errors:
                    response['errors'].append(self.format_error(e))

            if execution_result.invalid:
                status_code = 400
            else:
                response['data'] = execution_result.data

            if self.batch:
                response['id'] = id
                response['status'] = status_code

            response['code'] = status_code
            result = self.json_encode(request, response, pretty=show_graphiql)

        self.log_operation(request, status_code, operation_name, variables)

        return result, status_code


class ReactAppView(View):
    """Serves the compiled frontend entry point.
    """
    def get(self, request):
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )


class StaticAssetView(View):
    """Serves static assets in the production setting.
    """
    SUPPORTED_EXTENSIONS = {
        'js': {
            'content_type': 'application/javascript',
        },
        'json': {
            'content_type': 'application/json',
        },
        'yml': {
            'content_type': 'text/plain',
        },
        'html': {
            'content_type': 'text/html',
        },
        'css': {
            'content_type': 'text/css',
        },
        'txt': {
            'content_type': 'text/plain',
        },
        'map': {
            'content_type': 'application/octet-stream',
        },
        'ico': {
            'content_type': 'image/ico',
            'mode': 'rb',
        },
        'png': {
            'content_type': 'img/png',
            'mode': 'rb',
        },
        'jpg': {
            'content_type': 'img/jpeg',
            'mode': 'rb',
        },
    }

    def get(self, request, filepath):
        assetpath = os.path.join(settings.REACT_APP_DIR, 'build', filepath)
        extension = os.path.splitext(filepath)[1][1:]

        if extension not in self.SUPPORTED_EXTENSIONS:
            return HttpResponse('404', status=404)

        mode = self.SUPPORTED_EXTENSIONS[extension].get('mode', 'r')

        try:
            with open(assetpath, mode=mode) as f:
                content = f.read()
            response = HttpResponse(
                content,
                content_type=self.SUPPORTED_EXTENSIONS[extension]['content_type'],
                charset='utf-8',
            )
            response['Content-Length'] = len(content)
            return response
        except FileNotFoundError:
            return HttpResponse('404', status=404)
