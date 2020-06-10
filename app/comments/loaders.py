# -*- coding: utf-8 -*-
from promise import Promise
from promise.dataloader import DataLoader

from django.contrib.contenttypes.models import ContentType

from app.comments.models import Comment
from app.definitions.models import Column


class ColumnCommentCountLoader(DataLoader):
    """Preload the counts for provided comments.
    """
    def batch_load_fn(self, column_ids):
        """Function to process the batch load.
        """
        content_type = ContentType.objects.get_for_model(Column)

        mapping = {c: 0 for c in column_ids}
        results = (
            Comment.objects
                   .filter(object_id__in=column_ids)
                   .filter(content_type=content_type)
                   .filter(parent__isnull=True)
        )

        for comment in results:
            mapping[comment.object_id] += 1

        return Promise.resolve([
            mapping.get(c, 0) for c in column_ids
        ])


class ChildCommentLoader(DataLoader):
    """Preload child comments for provided parent comments.
    """
    def batch_load_fn(self, parent_comment_ids):
        """Function to process the batch load.
        """
        mapping = {t: [] for t in parent_comment_ids}
        results = Comment.objects.filter(parent_id__in=parent_comment_ids).order_by('-created_at')
        is_processed = set()

        for comment in results:
            if comment.pk in is_processed:
                continue
            mapping[comment.parent_id].append(comment)
            is_processed.add(comment.pk)

        return Promise.resolve([
            mapping.get(s, []) for s in parent_comment_ids
        ])
