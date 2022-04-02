# # -*- coding: utf-8 -*-
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response

# from app.api.permissions import IsAuthenticated


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_datastores(request, format=None):
#     """GET /api/v1/datastores
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_datastore(request, format=None):
#     """GET /api/v1/datastores/:datastoreId
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_datastore_tables(request, format=None):
#     """GET /api/v1/datastores/:datastoreId/tables
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)


# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def update_datastore(request, format=None):
#     """PATCH /api/v1/datastores/:datastoreId
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)


# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def update_datastore_properties(request, format=None):
#     """PATCH /api/v1/datastores/:datastoreId/properties
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)


# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])
# def update_datastore_owners(request, format=None):
#     """PATCH /api/v1/datastores/:datastoreId/owners
#     """
#     content = {
#         'status': 'request was permitted'
#     }
#     return Response(content)
