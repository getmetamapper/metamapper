# -*- coding: utf-8 -*-
from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from app.authentication.models import User, Workspace


class WorkspaceLoader(DataLoader):
    """Preload a collection of workspaces based on the pk field.
    """
    def batch_load_fn(self, workspace_ids):
        output = defaultdict(list)
        queryset = Workspace.objects.filter(id__in=workspace_ids)

        for workspace_id in workspace_ids:
            output[workspace_id] = next(filter(lambda q: q.id == workspace_id, queryset), None)

        return Promise.resolve([output.get(o) for o in workspace_ids])


class UserLoader(DataLoader):
    """Preload a collection of users based on the pk field.
    """
    def batch_load_fn(self, user_ids):
        output = defaultdict(list)
        queryset = User.objects.filter(id__in=user_ids)

        for user_id in user_ids:
            output[user_id] = next(filter(lambda q: q.id == user_id, queryset), None)

        return Promise.resolve([output.get(o) for o in user_ids])
