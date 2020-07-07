# -*- coding: utf-8 -*-
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import connection

from app.authentication.models import User
from app.authorization.models import Membership


@receiver(post_delete, sender=Membership)
def remove_revoked_user_from_groups(sender, instance, *args, **kwargs):
    """Removes active Group memberships when a User is removed from a Workspace.
    """
    user = User.objects.filter(
        email__iexact=instance.user_id,
    ).first()

    if user is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                DELETE FROM auth_users_groups u
                USING auth_group g
                WHERE g.id = u.group_id AND (g.workspace_id = %s AND u.user_id = %s)
                ''',
                [instance.workspace_id, user.id],
            )
