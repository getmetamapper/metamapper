# -*- coding: utf-8 -*-
import uuid
import unittest.mock as mock

from billiard.einfo import ExceptionInfo

import testutils.cases as cases
import testutils.factories as factories

import app.revisioner.tasks.core as tasks


class CoreRevisionerTaskCallbackTests(cases.TestCase):
    """Test cases for task error callbacks.
    """
    def test_start_revisioner_run(self):
        """Tests that the start_revisioner_run error callback works.
        """
        run = factories.RevisionerRunFactory()

        msg = "This is an error"
        exc = Exception(msg)
        task_id = "test_task_id"
        args = [run.id]
        einfo = ExceptionInfo

        s = mock.Mock(_run=run)

        tasks.on_start_revisioner_run_failure(s, exc, task_id, args, {}, einfo)

        error = run.errors.first()

        self.assertEqual(error.exc_message, msg)
        self.assertEqual(error.run_id, run.id)
        self.assertEqual(error.task_id, None)
        self.assertEqual(error.task_fcn, "start_revisioner_run")

    def test_revise_schema_definition_failure(self):
        """Tests that the revise_schema_definition error callback works.
        """
        run = factories.RevisionerRunFactory()
        run_task = run.tasks.create(meta_task_id=str(uuid.uuid4()), storage_path='/dummy')

        msg = "This is an error"
        exc = Exception(msg)
        task_id = "test_task_id"
        args = [run.id]
        einfo = ExceptionInfo

        s = mock.Mock(_run_task=run_task)

        tasks.on_revise_schema_definition_failure(s, exc, task_id, args, {}, einfo)

        error = run.errors.first()

        self.assertEqual(error.exc_message, msg)
        self.assertEqual(error.run_id, run.id)
        self.assertEqual(error.task_id, run_task.id)
        self.assertEqual(error.task_fcn, "revise_schema_definition")

    def test_commit_revisions_failure(self):
        """Tests that the on_commit_revisions_failure error callback works.
        """
        run = factories.RevisionerRunFactory()

        msg = "This is an error"
        exc = Exception(msg)
        task_id = "test_task_id"
        args = [run.id]
        einfo = ExceptionInfo

        s = mock.Mock(_run=run)

        tasks.on_commit_revisions_failure(s, exc, task_id, args, {}, einfo)

        error = run.errors.first()

        self.assertEqual(error.exc_message, msg)
        self.assertEqual(error.run_id, run.id)
        self.assertEqual(error.task_id, None)
        self.assertEqual(error.task_fcn, "commit_revisions")
