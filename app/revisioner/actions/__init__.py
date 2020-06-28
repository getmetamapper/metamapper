# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from app.revisioner.actions import created
from app.revisioner.actions import modified
from app.revisioner.actions import dropped


def commit_revisions(datastore, run, logger):
    """We will only ever commit revisions for the most recent run.
    """
    logger.info('Starting commit process.')

    if run.finished:
        logger.info('Run has already been committed.')
        return

    with transaction.atomic():
        total_created = 0
        for model_name, action_class in created.get_actions():
            logger.info(f'Starting commit process for created {model_name} objects.')
            action = action_class(run, datastore, logger)
            committed = len(action.apply())
            action.revisions.update(applied_on=timezone.now())
            total_created += committed

        total_modified = 0
        for model_name, action_class in modified.get_actions():
            logger.info(f'Starting commit process for modified {model_name} objects.')
            action = action_class(run, datastore, logger)
            committed = len(action.apply())
            action.revisions.update(applied_on=timezone.now())
            total_modified += committed

        total_dropped = 0
        for model_name, action_class in dropped.get_actions():
            logger.info(f'Starting commit process for dropped {model_name} objects.')
            action = action_class(run, datastore, logger)
            committed = action.apply()
            action.revisions.update(applied_on=timezone.now())
            total_dropped += committed

    logger.info('Run has been committed.')
