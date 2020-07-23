# -*- coding: utf-8 -*-
import json
import os
import six
import time

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from graphql import GraphQLError
from graphene_django.views import GraphQLView

from utils.errors import format_error as format_graphql_error
from utils.logging.graphql import get_request_logger
from utils.uploads import place_files_in_operations

from metamapper.loaders import GlobalDataLoader


logger = get_request_logger()


class MetamapperGraphQLView(GraphQLView):
    """Modified GraphQLView to inject workspace object into context.
    """
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

    def get_response(self, request, data, show_graphiql=False):
        """Handler for GraphQL response.
        """
        start_time = time.time()

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

        logger.log(request, response, operation_name, round((time.time() - start_time) * 1000, 2), **(variables or {}))

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
