# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from app.revisioner.actions import created
from app.revisioner.actions import modified
from app.revisioner.actions import dropped

from app.definitions.models import Column, Table
from app.revisioner.revisioners import get_content_type_for_model

from utils.shortcuts import run_raw_sql


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
    if run.is_datastore_first_run:
        run_raw_sql(
            '''
            DELETE FROM revisioner_revision
            WHERE applied_on IS NOT NULL
              AND action = 1
              AND resource_type_id = %(type)s
              AND run_id = %(run)s
            ''',
            {'type': get_content_type_for_model(Column).id, 'run': run.id},
        )

    logger.info('Run has been committed.')
