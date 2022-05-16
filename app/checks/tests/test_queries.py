# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers

import app.checks.tasks.expectations as expectations
import utils.shortcuts as shortcuts


class TestCheckExpectationHandlers(cases.GraphQLTestCase):
    """Test retrieval of the check expectation options.
    """
    operation = 'checkExpectationHandlers'
    statement = '''
    query GetCheckExpectationHandlers {
      checkExpectationHandlers {
        handler
        details {
          name
          type
          label
          options
          helpText
        }
      }
    }
    '''

    def test_execute(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]
        expects = [
            'app.checks.tasks.expectations.' + name for name in expectations.__all__
        ]

        self.assertEqual(expects, [
            r['handler'] for r in results
        ])


class TestCheckIntervalOptions(cases.GraphQLTestCase):
    """Test retrieval of the check interval options.
    """
    operation = 'checkIntervalOptions'
    statement = '''
    query GetCheckIntervalOptions {
      checkIntervalOptions {
        label
        value
      }
    }
    '''

    def test_execute(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {'label': '30 minutes', 'value': '0:30:00'},
            {'label': '1 hour', 'value': '1:00:00'},
            {'label': '2 hours', 'value': '2:00:00'},
            {'label': '4 hours', 'value': '4:00:00'},
            {'label': '6 hours', 'value': '6:00:00'},
            {'label': '12 hours', 'value': '12:00:00'},
            {'label': '1 day', 'value': '1 day, 0:00:00'},
            {'label': '3 days', 'value': '3 days, 0:00:00'},
            {'label': '7 days', 'value': '7 days, 0:00:00'},
            {'label': '30 days', 'value': '30 days, 0:00:00'},
        ])


class TestCheckAlertChannels(cases.GraphQLTestCase):
    """Test retrieval of the check alert channel options.
    """
    operation = 'checkAlertChannels'
    statement = '''
    query GetCheckAlertChannels {
      checkAlertChannels {
        label
        value
      }
    }
    '''

    def test_execute(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {'label': 'Email', 'value': 'EMAIL'},
        ])


class TestGetChecks(cases.GraphQLTestCase):
    """Test retrieval list of checks associated with a datastore.
    """
    operation = 'datastoreChecks'
    statement = '''
    query GetDatastoreChecks(
      $datastoreId: ID!
    ) {
      datastoreChecks: checks(datastoreId: $datastoreId) {
        edges {
          node {
            pk
            name
            isEnabled
            creator {
              name
            }
            lastExecution {
              status
              finishedAt
            }
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.datastore_id = helpers.to_global_id('DatastoreType', self.datastore.id)
        self.count = 10
        self.other_check = factories.CheckFactory(workspace=self.other_workspace)
        self.checks = factories.CheckFactory.create_batch(self.count, datastore=self.datastore)

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        results = self.execute(self.statement, variables={'datastoreId': self.datastore_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of active checks.',
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg='Node count should equal totalCount field.',
        )

        self.assertNotIn(self.other_check.pk, [
            edge['node']['pk'] for edge in results['edges']
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')
        self.datastore.save()

        results = self.execute(self.statement, variables={'datastoreId': self.datastore_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of active checks.',
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled_and_not_granted(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(self.statement, variables={'datastoreId': self.datastore_id}))

    @decorators.as_someone(['OWNER'])
    def test_with_object_permissions_enabled_and_owner(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables={'datastoreId': self.datastore_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of active checks.',
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'datastoreId': self.datastore_id}))


class TestGetCheck(cases.GraphQLTestCase):
    """Test retrieval of a single check by ID.
    """
    operation = 'datastoreCheck'
    statement = '''
    query GetDatastoreCheck(
      $id: ID!
    ) {
      datastoreCheck: check(id: $id) {
        id
        name
        isEnabled
        shortDesc
        tags
        interval {
          label
          value
        }
        creator {
          name
          email
        }
        query {
          sqlText
        }
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.checkdata = {
            'creator': self.owner,
            'datastore': self.datastore,
            'name': 'Data Quality Check V1',
            'short_desc': 'International bill throw role.',
            'tags': ['one', 'two', 'three'],
        }
        self.query = factories.CheckQueryFactory(sql_text="SELECT COUNT(1) FROM app.users", workspace=self.workspace)
        self.check = factories.CheckFactory(query=self.query, **self.checkdata)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)

    def assertExpectedResults(self, results):
        """It should output the correct result body.
        """
        self.assertEqual(results['data'][self.operation], {
            'id': self.check_id,
            'name': self.checkdata['name'],
            'isEnabled': True,
            'shortDesc': self.checkdata['short_desc'],
            'tags': ['one', 'two', 'three'],
            'interval': {'label': '1 hour', 'value': '1:00:00'},
            'creator': {'name': 'Sam Crust', 'email': 'owner@metamapper.io'},
            'query': {'sqlText': "SELECT COUNT(1) FROM app.users"},
        })

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        self.assertExpectedResults(
            self.execute(self.statement, variables={'id': self.check_id}))

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')
        self.datastore.save()

        self.assertExpectedResults(
            self.execute(self.statement, variables={'id': self.check_id}))

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled_and_not_granted(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(self.statement, variables={'id': self.check_id}))

    @decorators.as_someone(['OWNER'])
    def test_with_object_permissions_enabled_and_owner(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertExpectedResults(
            self.execute(self.statement, variables={'id': self.check_id}))

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'id': self.check_id}))

    @decorators.as_someone(['OWNER'])
    def test_not_found(self):
        node_id = helpers.to_global_id('CheckType', 'abcdefghi')
        results = self.execute(self.statement, variables={'id': node_id})
        self.assertNotFound(results)


class TestGetCheckExpectations(cases.GraphQLTestCase):
    """Test retrieval of expectations associated with a check.
    """
    operation = 'checkExpectations'
    statement = '''
    query GetCheckExpectations(
      $checkId: ID!
    ) {
      checkExpectations(checkId: $checkId) {
        edges {
          node {
            pk
            description
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)
        self.count = 4
        self.expectations = factories.CheckExpectationFactory.create_batch(self.count, job=self.check)
        self.other_check = factories.CheckFactory(workspace=self.other_workspace)
        self.other_expectation = factories.CheckExpectationFactory(job=self.other_check)

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg='Node count should equal totalCount field.',
        )

        self.assertNotIn(self.other_expectation.pk, [
            edge['node']['pk'] for edge in results['edges']
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled_and_not_granted(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))

    @decorators.as_someone(['OWNER'])
    def test_with_object_permissions_enabled_and_owner(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))


class TestGetCheckExecutions(cases.GraphQLTestCase):
    """Test retrieval of check executions.
    """
    operation = 'checkExecutions'
    statement = '''
    query GetCheckExecutions(
      $checkId: ID!
    ) {
      checkExecutions(checkId: $checkId, first: 10) {
        edges {
          node {
            pk
            status
            failsCount
            tasksCount
            startedAt
            finishedAt
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)
        self.count = 10
        self.executions = [
            factories.CheckExecutionFactory(
                job=self.check,
                epoch=shortcuts.epoch_now() + i,
                started_at=datetime(2022, 1, 24, 1, 1, 1).astimezone(timezone.utc),
            )
            for i in range(self.count)
        ]
        self.other_check = factories.CheckFactory(workspace=self.other_workspace)
        self.other_execution = factories.CheckExecutionFactory(job=self.other_check)

    @decorators.as_someone(['OWNER'])
    def test_query(self):
        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg='Node count should equal totalCount field.',
        )

        self.assertNotIn(self.other_execution.pk, [
            edge['node']['pk'] for edge in results['edges']
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled_and_not_granted(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))

    @decorators.as_someone(['OWNER'])
    def test_with_object_permissions_enabled_and_owner(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))


class TestGetCheckExecution(cases.GraphQLTestCase):
    """Test retrieval of check execution.
    """
    operation = 'checkExecution'
    statement = '''
    query GetCheckExecution(
      $id: ID!
    ) {
      checkExecution(id: $id) {
        id
        status
        error
        startedAt
        finishedAt
        executedQueryText
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.query = factories.CheckQueryFactory(workspace=self.workspace, sql_text='SELECT id FROM auth_workspaces')
        self.check = factories.CheckFactory(datastore=self.datastore, query=self.query)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)
        self.expectation = factories.CheckExecutionFactory(
            job=self.check,
            query=self.query,
            epoch=1650851215,
            started_at=datetime(2022, 4, 25).astimezone(timezone.utc),
            finished_at=(datetime(2022, 4, 25) + timedelta(seconds=25)).astimezone(timezone.utc))
        self.expectation_id = helpers.to_global_id('CheckExecutionType', self.expectation.id)

    def assertExpectedResults(self, results):
        """It should output the correct result body.
        """
        self.assertEqual(results['data'][self.operation], {
            'id': self.expectation_id,
            'status': 'SUCCESS',
            'error': None,
            'startedAt': '2022-04-25T00:00:00+00:00',
            'finishedAt': '2022-04-25T00:00:25+00:00',
            'executedQueryText': 'SELECT id FROM auth_workspaces',
        })

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        self.assertExpectedResults(
            self.execute(self.statement, variables={'id': self.expectation_id}))

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'id': self.expectation_id}))

    @decorators.as_someone(['OWNER'])
    def test_not_found(self):
        node_id = helpers.to_global_id('CheckExecutionType', 123456789)
        results = self.execute(self.statement, variables={'id': node_id})
        self.assertNotFound(results)


class TestGetCheckAlertRules(cases.GraphQLTestCase):
    """Test retrieval of check alert rules.
    """
    operation = 'checkAlertRules'
    statement = '''
    query GetCheckAlertRules(
      $checkId: ID!
    ) {
      checkAlertRules(checkId: $checkId) {
        edges {
          node {
            pk
            name
            channel
            channelConfig
            createdAt
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)
        self.count = 5
        self.alert_rules = [
            factories.CheckAlertRuleFactory(job=self.check) for i in range(self.count)
        ]
        self.other_check = factories.CheckFactory(workspace=self.other_workspace)
        self.other_alert_rule = factories.CheckAlertRuleFactory(job=self.other_check)

    @decorators.as_someone(['OWNER'])
    def test_query(self):
        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check alert rules.',
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg='Node count should equal totalCount field.',
        )

        self.assertNotIn(self.other_alert_rule.pk, [
            edge['node']['pk'] for edge in results['edges']
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_enabled_and_not_granted(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))

    @decorators.as_someone(['OWNER'])
    def test_with_object_permissions_enabled_and_owner(self):
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables={'checkId': self.check_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of check expectations.',
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'checkId': self.check_id}))


class TestGetCheckAlertRule(cases.GraphQLTestCase):
    """Test retrieval of check alert rule.
    """
    operation = 'checkAlertRule'
    statement = '''
    query GetCheckAlertRule(
      $id: ID!
    ) {
      checkAlertRule(id: $id) {
        id
        name
        channel
        channelConfig
        lastFailure {
          id
        }
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)
        self.check_execution = factories.CheckExecutionFactory(
            job=self.check,
            epoch=shortcuts.epoch_now(),
            started_at=datetime(2022, 1, 24, 1, 1, 1).astimezone(timezone.utc),
        )
        self.check_execution_id = helpers.to_global_id('CheckExecutionType', self.check_execution.id)
        self.alert_rule = factories.CheckAlertRuleFactory(
            job=self.check,
            name='Test Alert',
            last_failure=self.check_execution)
        self.alert_rule_id = helpers.to_global_id('CheckAlertRuleType', self.alert_rule.id)

    def assertExpectedResults(self, results):
        """It should output the correct result body.
        """
        self.assertEqual(results['data'][self.operation], {
            'id': self.alert_rule_id,
            'name': 'Test Alert',
            'channel': 'EMAIL',
            'channelConfig': {'emails': ['test@metamapper.io']},
            'lastFailure': {
                'id': self.check_execution_id,
            }
        })

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        self.assertExpectedResults(
            self.execute(self.statement, variables={'id': self.alert_rule_id}))

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'id': self.alert_rule_id}))

    @decorators.as_someone(['OWNER'])
    def test_not_found(self):
        node_id = helpers.to_global_id('CheckAlertRuleType', 123456789)
        results = self.execute(self.statement, variables={'id': node_id})
        self.assertNotFound(results)
