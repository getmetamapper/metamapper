# -*- coding: utf-8 -*-
import factory
import pandas as pd
import unittest.mock as mock

import app.checks.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers

from freezegun import freeze_time


def build_expectation_input(**overrides):
    """Helper method to build expectation input.
    """
    attrs = factory.build(dict, FACTORY_CLASS=factories.CheckExpectationFactory)
    attrs.update(**overrides)

    return {
        'handlerClass': attrs['handler_class'],
        'handlerInput': attrs['handler_input'],
        'passValueClass': attrs['pass_value_class'],
        'passValueInput': attrs['pass_value_input'],
    }


class CreateCheckTests(cases.GraphQLTestCase):
    """Tests for creating a datastore check.
    """
    factory = factories.CheckFactory

    operation = 'createCheck'
    statement = '''
    mutation CreateCheck(
      $datastoreId: ID!
      $queryId: ID!
      $name: String!
      $tags: [String]
      $shortDesc: String
      $interval: String!
      $expectations: [CheckExpectation]!
    ) {
      createCheck(input: {
        datastoreId: $datastoreId
        queryId: $queryId
        name: $name
        tags: $tags
        shortDesc: $shortDesc
        interval: $interval
        expectations: $expectations
      }) {
        check {
          name
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.datastore_id = helpers.to_global_id('DatastoreType', self.datastore.id)

        self.query = factories.CheckQueryFactory(datastore=self.datastore)
        self.query_id = helpers.to_global_id('CheckQueryType', self.query.id)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'datastoreId': self.datastore_id,
            'queryId': self.query_id,
            'name': helpers.faker.name(),
            'interval': '1:00:00',
            'expectations': [
                build_expectation_input(),
            ],
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should create a Check scoped to Workspace.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'check': {'name': variables['name']},
            'errors': None,
        })

    @decorators.as_someone(['OWNER'])
    def test_empty_expectations(self):
        """It should throw a validation error.
        """
        response = self.execute(variables=self._get_attributes(expectations=[]))
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'check': None,
            'errors': [
                {
                    'resource': 'Check',
                    'field': 'expectations',
                    'code': 'empty',
                }
            ],
        })

    @decorators.as_someone(['OWNER'])
    def test_bad_query_id(self):
        """It should throw a validation error.
        """
        response = self.execute(variables=self._get_attributes(queryId='VGVzdEJhZFR5cGU6MTIzNDU2Nzg5'))
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'check': None,
            'errors': [
                {
                    'resource': 'Check',
                    'field': 'query_id',
                    'code': 'exists',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))

    @decorators.as_someone(['OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class UpdateCheckTests(cases.GraphQLTestCase):
    """Tests for updating an existing datastore check.
    """
    factory = factories.CheckFactory

    operation = 'updateCheck'
    statement = '''
    mutation UpdateCheck(
      $id: ID!
      $name: String
      $tags: [String]
      $isEnabled: Boolean
      $shortDesc: String
      $interval: String
    ) {
      updateCheck(input: {
        id: $id
        name: $name
        tags: $tags
        isEnabled: $isEnabled
        shortDesc: $shortDesc
        interval: $interval
      }) {
        check {
          name
          isEnabled
          interval {
            label
            value
          }
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should update a check resource.
        """
        resource = self.factory(workspace=self.workspace, name='Meow Meow', interval='1:00:00')
        globalid = helpers.to_global_id('CheckType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
            'isEnabled': False,
            'interval': '2:00:00',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'check': {
                'name': variables['name'],
                'isEnabled': variables['isEnabled'],
                'interval': {
                    'label': '2 hours',
                    'value': variables['interval'],
                },
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            name=variables['name'],
            isEnabled=variables['isEnabled'],
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CheckType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
        }

        resource.datastore.object_permissions_enabled = True
        resource.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=variables))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CheckType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
        }

        self.assertPermissionDenied(
            self.execute(variables=variables))


class DeleteCheckTests(cases.GraphQLTestCase):
    """Tests for deleting an existing datastore check.
    """
    factory = factories.CheckFactory

    operation = 'deleteCheck'
    statement = '''
    mutation DeleteCheck($id: ID!) {
      deleteCheck(input: { id: $id }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER', 'MEMBER'])
    def test_valid(self):
        """It should permanently delete the check.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CheckType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Check,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        resource.datastore.object_permissions_enabled = True
        resource.datastore.save()

        globalid = helpers.to_global_id('CheckType', resource.pk)

        self.assertPermissionDenied(
            self.execute(variables={'id': globalid}))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CheckType', resource.pk)

        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)


class PreviewCheckQueryTests(cases.GraphQLTestCase):
    """Tests for previewing a check query.
    """
    factory = factories.CheckFactory

    operation = 'previewCheckQuery'
    statement = '''
    mutation PreviewCheckQuery(
      $datastoreId: ID!
      $interval: String!
      $sqlText: String!
    ) {
      previewCheckQuery(
        input: {
          id: $datastoreId,
          interval: $interval
          sqlText: $sqlText
        }
      ) {
        query {
          columns
        }
        queryResults
        sqlException
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.datastore_id = helpers.to_global_id('DatastoreType', self.datastore.id)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'datastoreId': self.datastore_id,
            'interval': '1:00:00',
            'sqlText': "SELECT COUNT(1) as cnt FROM app.workspaces WHERE created_at > '{{ ds }}'"
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch('app.inspector.service.get_engine')
    @mock.patch('app.inspector.service.get_dataframe')
    def test_valid(self, get_dataframe, get_engine):
        get_dataframe.return_value = pd.DataFrame([{'cnt': 100}])
        get_engine.return_value = mock.MagicMock(catchable_errors=[])

        with freeze_time("2021-05-17"):
            response = self.execute(variables=self._get_attributes())
            response = response['data'][self.operation]

            self.assertEqual(response, {
                'query': {'columns': ['cnt']},
                'queryResults': [{'cnt': 100}],
                'sqlException': None,
                'errors': None,
            })

            get_dataframe.assert_called_with(
                datastore=self.datastore,
                sql="SELECT COUNT(1) as cnt FROM app.workspaces WHERE created_at > '2021-05-17'",
                record_limit=50)

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))

    @decorators.as_someone(['OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class PreviewCheckExpectationTests(cases.GraphQLTestCase):
    """Tests for previewing a check expectation.
    """
    factory = factories.CheckFactory

    operation = 'previewCheckExpectation'
    statement = '''
    mutation PreviewCheckExpectation(
      $handlerClass: String!
      $handlerInput: JSONObject!
      $passValueClass: String!
      $passValueInput: JSONObject!
    ) {
      previewCheckExpectation(input: {
        handlerClass: $handlerClass,
        handlerInput: $handlerInput,
        passValueClass: $passValueClass,
        passValueInput: $passValueInput,
      }) {
        expectation {
          description
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def test_valid(self):
        """It should produce the description of the given expectation.
        """
        variables = {
            'handlerClass': 'app.checks.tasks.expectations.AssertAvgValueOfColumnToBe',
            'handlerInput': {'column': 'revenue', 'op': 'greater than', 'skipna': False},
            'passValueClass': 'app.checks.tasks.pass_values.Constant',
            'passValueInput': {'value': 10},
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]
        response = response['expectation']['description']

        self.assertEqual(
            response,
            'Expect the average of the `revenue` column to be greater than 10.')


class CreateCheckExpectationTests(cases.GraphQLTestCase):
    """Tests for creating a check expectation.
    """
    factory = factories.CheckExpectationFactory

    operation = 'createCheckExpectation'
    statement = '''
    mutation CreateCheckExpectation(
      $id: ID!
      $handlerClass: String!
      $handlerInput: JSONObject!
      $passValueClass: String!
      $passValueInput: JSONObject!
    ) {
      createCheckExpectation(input: {
        id: $id
        handlerClass: $handlerClass,
        handlerInput: $handlerInput,
        passValueClass: $passValueClass,
        passValueInput: $passValueInput,
      }) {
        expectation {
          handlerClass
          passValueClass
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attrs = build_expectation_input(**overrides)
        attrs.update({'id': self.check_id})
        return attrs

    @decorators.as_someone(['OWNER', 'MEMBER'])
    def test_valid(self):
        """It should create an Expectation scoped to a Check.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'expectation': {
                'handlerClass': variables['handlerClass'],
                'passValueClass': variables['passValueClass'],
            },
            'errors': None,
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))

    @decorators.as_someone(['OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class DeleteCheckExpectationTests(cases.GraphQLTestCase):
    """Tests for deleting a check expectation.
    """
    factory = factories.CheckExpectationFactory

    operation = 'deleteCheckExpectation'
    statement = '''
    mutation DeleteCheckExpectation($id: ID!) {
      deleteCheckExpectation(input: { id: $id }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)

    @decorators.as_someone(['OWNER', 'MEMBER'])
    def test_valid(self):
        """It should permanently delete the check expectation.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckExpectationType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.CheckExpectation,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(job=self.check)

        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        globalid = helpers.to_global_id('CheckExpectationType', resource.pk)

        self.assertPermissionDenied(
            self.execute(variables={'id': globalid}))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CheckExpectationType', resource.pk)

        self.assertPermissionDenied(
            self.execute(variables={'id': globalid}))


class CreateCheckAlertRuleTests(cases.GraphQLTestCase):
    """Tests for creating a check alert rule.
    """
    factory = factories.CheckAlertRuleFactory

    operation = 'createCheckAlertRule'
    statement = '''
    mutation CreateCheckAlertRule(
      $id: ID!
      $name: String!
      $interval: String!
      $channel: String!
      $channelConfig: JSONObject!
    ) {
      createCheckAlertRule(input: {
        id: $id
        name: $name
        interval: $interval
        channel: $channel
        channelConfig: $channelConfig
      }) {
        alertRule {
          name
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)
        self.check_id = helpers.to_global_id('CheckType', self.check.id)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'id': self.check_id,
            'name': helpers.faker.name(),
            'interval': '1:00:00',
            'channel': 'EMAIL',
            'channelConfig': {'emails': ['test1@metamapper.io', 'test2@metamapper.io']}
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should create an alert rule scoped to a check.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'alertRule': {'name': variables['name']},
            'errors': None,
        })


    @decorators.as_someone(['OWNER'])
    def test_invalid_channel_config(self):
        """It should throw a validation error.
        """
        bad_config = {
            'other_attributes': 12345,
        }

        response = self.execute(variables=self._get_attributes(channelConfig=bad_config))
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'alertRule': None,
            'errors': [
                {
                    'resource': 'CheckAlertRule',
                    'field': 'emails',
                    'code': 'required',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))

    @decorators.as_someone(['OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class UpdateCheckAlertRuleTests(cases.GraphQLTestCase):
    """Tests for updating an existing check alert rule.
    """
    factory = factories.CheckAlertRuleFactory

    operation = 'updateCheckAlertRule'
    statement = '''
    mutation UpdateCheckAlertRule(
      $id: ID!
      $name: String
      $interval: String
      $channelConfig: JSONObject
    ) {
      updateCheckAlertRule(input: {
        id: $id
        name: $name
        interval: $interval
        channelConfig: $channelConfig
      }) {
        alertRule {
          name
          interval {
            label
            value
          }
          channelConfig
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should update a check resource.
        """
        resource = self.factory(job=self.check, name='Meow Meow', interval='1:00:00')
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
            'interval': '2:00:00',
            'channelConfig': {'emails': ['scott.test@metamapper.io']},
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'alertRule': {
                'name': variables['name'],
                'interval': {
                    'label': '2 hours',
                    'value': variables['interval'],
                },
                'channelConfig': variables['channelConfig'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            name=variables['name'],
            channelConfig=variables['channelConfig'],
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
        }

        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables=variables))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'Woof Woof',
        }

        self.assertPermissionDenied(
            self.execute(variables=variables))


class DeleteCheckAlertRuleTests(cases.GraphQLTestCase):
    """Tests for deleting a check alert rule.
    """
    factory = factories.CheckAlertRuleFactory

    operation = 'deleteCheckAlertRule'
    statement = '''
    mutation DeleteCheckAlertRule($id: ID!) {
      deleteCheckAlertRule(input: { id: $id }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''
    def setUp(self):
        super().setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.check = factories.CheckFactory(datastore=self.datastore)

    @decorators.as_someone(['OWNER', 'MEMBER'])
    def test_valid(self):
        """It should permanently delete the check alert rule.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.CheckAlertRule,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER', 'MEMBER'])
    def test_unauthorized_object_permissions_enabled(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.assertPermissionDenied(
            self.execute(variables={'id': globalid}))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(job=self.check)
        globalid = helpers.to_global_id('CheckAlertRuleType', resource.pk)

        self.assertPermissionDenied(
            self.execute(variables={'id': globalid}))
