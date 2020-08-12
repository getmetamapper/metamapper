# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from app.revisioner.actions import created
from app.revisioner.actions import modified
from app.revisioner.actions import dropped

from app.definitions.models import Column
from app.revisioner.revisioners import get_content_type_for_model


def commit_revisions(datastore, run, logger):
    """We will only ever commit revisions for the most recent run.
    """
    logger.info('Starting commit process.')

    if run.finished:
        logger.info('Run has already been committed.')
        return

    with transaction.atomic():
        for model_name, action_class in created.get_actions():
            logger.info(f'Starting commit process for created {model_name} objects.')
            action = action_class(run, datastore, logger)
            action.apply()
            action.revisions.update(applied_on=timezone.now())

        for model_name, action_class in modified.get_actions():
            logger.info(f'Starting commit process for modified {model_name} objects.')
            action = action_class(run, datastore, logger)
            action.apply()
            action.revisions.update(applied_on=timezone.now())

        for model_name, action_class in dropped.get_actions():
            logger.info(f'Starting commit process for dropped {model_name} objects.')
            action = action_class(run, datastore, logger)
            action.apply()
            action.revisions.update(applied_on=timezone.now())

    # We remove all of the "Column was created" revisions because they aren't super
    # useful from a debugging or UI perspective.
    # if run.is_datastore_first_run:
    resource_type = get_content_type_for_model(Column)
    run.revisions.created(unapplied_only=False).filter(resource_type=resource_type).delete()

    logger.info('Run has been committed.')
