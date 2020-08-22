# -*- coding: utf-8 -*-
import copy
import glob
import os
import shutil
import unittest.mock as mock

import app.revisioner.tasks as core
import app.revisioner.models as models
import app.revisioner.revisioners as revisioners

from django.conf import settings
from django.utils import timezone
from django.core.management import call_command

from app.definitions.models import Datastore
from metamapper.celery import app as celery_app

from django.test import TestCase

from utils.contenttypes import get_content_types


cmd_folder = os.path.join(os.path.dirname(__file__), 'e2e')


def clean_uploads_folder(datastore_id, run_id):
    """Once the tests have ran, we should remove all files from `uploads/` directory.
    """
    root_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'revisioner')
    run_path = os.path.join(root_dir, datastore_id, 'run_id=%s' % run_id)

    if os.path.isdir(run_path):
        shutil.rmtree(run_path)


class End2EndRevisionerTests(TestCase):
    """Loads test fixtures from `e2e` directory and executes them.
    """
    def test_celery_always_eager(self):
        """CELERY_ALWAYS_EAGER should be set to True
        """
        assert celery_app.conf.task_always_eager

    def execute_test(self, fixtures, cases, filename):
        """Execute the test.
        """
        call_command('flush', interactive=False)
        call_command('loaddata', *fixtures, **{'verbosity': 0})

        datastore = Datastore.objects.get(slug='metamapper')

        run = models.Run.objects.create(
            workspace_id=datastore.workspace_id,
            datastore_id=datastore.id,
            started_at=timezone.now(),
        )

        try:
            core.start_revisioner_run(run.id)
        finally:
            clean_uploads_folder(datastore.id, run.id)

        content_types = get_content_types()

        for case in cases:
            resource = None
            if 'model' in case:
                resource = (
                    content_types[case['model']].model_class()
                                                .objects
                                                .filter(**case.get('filters', {}))
                                                .first()
                )
            for assertion in case['assertions']:
                message = '\n'.join([
                    filename,
                    case['description'],
                    assertion.get('summarized', ''),
                ])

                evaluated = assertion['evaluation'](datastore, resource)
                self.assertEqual(
                    evaluated,
                    assertion['pass_value'],
                    message,
                )


def create_test(fn, filename):
    """Helper function to create a e2e test based on the filename.
    """
    @mock.patch('app.inspector.service.tables_and_views')
    @mock.patch('app.inspector.service.indexes')
    @mock.patch('app.inspector.service.version')
    def do_test_expected(self, mock_version, mock_indexes, mock_tables):
        """Execute the internal test based on the provided file.
        """
        ns = {}

        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)

        mock_tables.return_value = sorted(ns['inspected_tables'], key=lambda r: (r['table_schema'], r['table_name']))
        mock_indexes.return_value = ns['inspected_indexes']
        mock_version.return_value = '1.0.0'

        if len(ns['inspected_tables']):
            self.execute_test(
                fixtures=list(set(['core.json'] + ns['preload_fixtures'])),
                cases=ns['test_cases'],
                filename=filename,
            )
    return do_test_expected


def mutate_modified(record, rule):
    """Mutate a record for a "MODIFIED" action.
    """
    field = rule['metadata']['field']
    new_value = rule['metadata']['new_value']
    if '.' in field:
        f, n = field.split('.')
    else:
        f, n = (field, None)
    if not rule['filters'](record) or f not in record:
        return record
    if isinstance(record[f], dict):
        record[f][n] = new_value
    elif isinstance(record[f], list):
        for column in record[f]:
            if rule.get('column_filters', lambda c: False)(column):
                column[n] = new_value
    else:
        record[f] = new_value
    return record


def mutate_dropped(record, rule):
    """Mutate a record for a "DROPPED" action.
    """
    if rule['filters'](record):
        r = copy.copy(record)
        c = []
        if 'column_filters' not in rule:
            return None
        for column in r['columns']:
            c_filters = rule.get('column_filters', lambda c: False)
            if not c_filters(column):
                c.append(column)
            r['columns'] = c
        return r
    return record


def mutate_created(record, rule):
    """Mutate a record for a "CREATED" action.
    """
    return record


def mutate_inspected(records, rules):
    """Mutate the inspected records to meet test specifications.
    """
    records = copy.deepcopy(records)
    mapping = {
        'created': mutate_created,
        'dropped': mutate_dropped,
        'modified': mutate_modified,
    }
    output = []
    for record in records:
        r = copy.deepcopy(record)
        for rule in rules:
            if r:
                r = mapping[rule['type']](r, rule)
        if r:
            output.append(r)
    return output


for filepath in glob.glob(cmd_folder + '/e2e_*.py'):
    fname, ext = os.path.splitext(filepath)
    setattr(
        End2EndRevisionerTests,
        'test_%s' % fname,
        create_test(filepath, fname),
    )
