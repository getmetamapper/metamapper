# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from app.revisioner.actions import created
from app.revisioner.actions import modified
from app.revisioner.actions import dropped


def commit_revisions(datastore, run, logger):
    """We will only ever commit revisions for the most recent run.
    """
    logger.info('Starting commit process')

    if run.finished:
        logger.info('Run has already been committed')
        return

    with transaction.atomic():
        total_created = 0
        # logger.info('Run<{}> running for CREATE actions.'.format(run.id))
        for model_name, action_class in created.get_actions():
            action = action_class(run, datastore)
            committed = len(action.apply())
            action.revisions.update(applied_on=timezone.now())
            # logger.info('CREATED<{}>: {}'.format(model_name, committed))
            total_created += committed

        total_modified = 0
        # logger.info('Run<{}> running for MODIFIED actions.'.format(run.id))
        for model_name, action_class in modified.get_actions():
            action = action_class(run, datastore)
            committed = len(action.apply())
            action.revisions.update(applied_on=timezone.now())
            # logger.info('MODIFIED<{}>: {}'.format(model_name, committed))
            total_modified += committed

        total_dropped = 0
        # logger.info('Run<{}> running for DROP actions.'.format(run.id))
        for model_name, action_class in dropped.get_actions():
            action = action_class(run, datastore)
            committed = action.apply()
            action.revisions.update(applied_on=timezone.now())
            # logger.info('DROPPED<{}>: {}'.format(model_name, committed))
            total_dropped += committed

        # logger.info('C: {}, M: {}, D: {}'.format(total_created, total_modified, total_dropped))

    logger.info('Run has been committed')
