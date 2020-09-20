# -*- coding: utf-8 -*-
from promise import Promise
from promise.dataloader import DataLoader

from app.comments.models import Comment
from app.definitions.models import Column, Table

from utils.contenttypes import get_content_types


class OmnisearchResultLoader(DataLoader):
    """Prefetch search results based on the provided metadata.
    """

    def batch_load_fn(self, result_tuples):
        """Input is provided as a list of tuples: ("pk", "model_name",)
        """
        content_types = get_content_types()

        ident = {'Column': [], 'Table': [], 'Comment': []}
        for pk, model_name in result_tuples:
            ident[model_name].append(pk)

        instances = {}

        instances['Table'] = {
            i.pk: i.as_search_result()
            for i in Table.objects.filter(id__in=ident['Table']).select_related('schema')
        }

        instances['Column'] = {
            i.pk: i.as_search_result()
            for i in Column.objects.filter(id__in=ident['Column']).select_related('table', 'table__schema')
        }

        table_comments = (
            Comment.objects
                   .filter(id__in=ident['Comment'])
                   .filter(content_type=content_types['Table'])
                   .prefetch_related('content_object', 'content_object__schema')
        )

        table_comments_dict = {
            i.pk: i.as_search_result()
            for i in table_comments
        }

        column_comments = (
            Comment.objects
                   .filter(id__in=ident['Comment'])
                   .filter(content_type=content_types['Column'])
                   .prefetch_related('content_object', 'content_object__table', 'content_object__table__schema')
        )

        column_comments_dict = {
            i.pk: i.as_search_result()
            for i in column_comments
        }

        instances['Comment'] = {**table_comments_dict, **column_comments_dict}

        return Promise.resolve([
            instances[model_name].get(pk)
            for pk, model_name in result_tuples
        ])
