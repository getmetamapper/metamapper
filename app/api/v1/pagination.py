# -*- coding: utf-8 -*-
from base64 import b64encode
from collections import OrderedDict
from urllib import parse

from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class CursorSetPagination(CursorPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    ordering = '-created_at'
    count = None

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_count(self, queryset):
        try:
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next_page_token', self.get_next_link()),
            ('prev_page_token', self.get_previous_link()),
            ('page_info', self.get_page_info()),
            ('items', data)
        ]))

    def get_page_info(self):
        return OrderedDict([
            ('total_results', self.count),
            ('results_per_page', self.page_size),
        ])

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'next_page_token': {
                    'type': 'string',
                    'nullable': True,
                },
                'prev_page_token': {
                    'type': 'string',
                    'nullable': True,
                },
                'page_info': {
                    'type': 'object',
                    'properties': {
                        'total_results': {
                            'type': 'integer',
                            'nullable': False,
                        },
                        'results_per_page': {
                            'type': 'integer',
                            'nullable': False,
                        },
                    },
                },
                'items': schema,
            },
        }

    def encode_cursor(self, cursor):
        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = parse.urlencode(tokens, doseq=True)
        return b64encode(querystring.encode('ascii')).decode('ascii')
