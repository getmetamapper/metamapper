# -*- coding: utf-8 -*-
import os

import app.checks.models as models
import app.inspector.service as inspector

import utils.blob as blob
import utils.logging as logging


logger = logging.getLogger(__name__)


class CheckExecutor(object):
    """Execute a check against its expectations.
    """
    def __init__(self, check_execution, upload_archive=True):
        self.check_execution = check_execution
        self.check = self.check_execution.job
        self.datastore = self.check.datastore
        self.query = self.check.query
        self.query_template = self.query.to_template()
        self.upload_archive = upload_archive
        self.engine = inspector.get_engine(self.datastore)

    def get_expectations(self):
        """Return only enabled expectations for the check.
        """
        return self.check.expectations.filter(deleted_at__isnull=True).order_by('created_at')

    def get_dataframe(self, context):
        """DataFrame: Execute templated query and return dataframe
        """
        get_kwargs = {
            'datastore': self.datastore,
            'sql': self.query_template.render(**context.to_dict()),
        }
        return inspector.get_dataframe(**get_kwargs)

    def commit_expectation_results(self, expectation_results):
        """void: Commit the expectation results to the database.
        """
        for expectation_result in expectation_results:
            expectation_result.execution_id = self.check_execution.id

        models.CheckExpectationResult.objects.bulk_create(expectation_results, ignore_conflicts=True)

    def archive_dataframe_to_file_storage(self, dataframe):
        """void: Upload the dataframe via FileStorage backend.
        """
        parts = (
            "checks",
            self.datastore.id,
            f"check_id={self.check.id}",
            f"epoch={self.check_execution.epoch}",
            "dataframe.json.gz",
        )
        blob.put_object(os.path.join(*parts), dataframe.to_dict(orient='split'))

    def execute(self, context):
        """void: Execute the check with the provided context.
        """
        expectations = self.get_expectations()

        if not len(expectations):
            self.check.is_enabled = False
            self.check.save()
            self.check_execution.delete()
            return

        error = None
        fails = len(expectations)

        try:
            dataframe = self.get_dataframe(context=context)
            expectation_results = []
            for expectation in expectations:
                expectation_result = expectation.do_check(dataframe)
                expectation_results.append(expectation_result)
                if expectation_result.passed:
                    fails -= 1
            self.commit_expectation_results(expectation_results)
        except self.engine.catchable_errors as exc:
            error = str(exc)
        except Exception as exc:
            error = 'An unexpected error has occurred.'
            logger.error(str(exc))

        self.check_execution.error = error
        self.check_execution.mark_as_finished(fails_count=fails)

        if not error and self.upload_archive:
            self.archive_dataframe_to_file_storage(dataframe)
