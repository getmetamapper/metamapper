import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Card, Col, Form, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { ellipsis } from "lib/utilities"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import UpdateCheckAlertRuleMutation from "graphql/mutations/UpdateCheckAlertRule"
import CheckAlertRuleEditForm from "app/Datastores/DatastoreChecks/CheckAlertRuleEditForm"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetDatastoreCheck from "graphql/withGetDatastoreCheck"
import withGetCheckAlertRule from "graphql/withGetCheckAlertRule"
import withGetCheckAlertRuleOptions from "graphql/withGetCheckAlertRuleOptions"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreCheckAlertRuleEdit extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      check,
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    return [
      {
        label: "Datastores",
        to: `/${slug}/datastores`,
      },
      {
        label: datastoreSlug,
        to: `/${slug}/datastores/${datastoreSlug}`,
      },
      {
        label: "Checks",
        to: `/${slug}/datastores/${datastoreSlug}/checks`,
      },
      {
        label: ellipsis(check.name),
        to: `/${slug}/datastores/${datastoreSlug}/checks/${check.pk}`,
      },
      {
        label: 'New Alert Rule',
      },
    ]
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { checkAlertRule: { id } } = this.props

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: {
          id,
          ...variables,
        },
        successMessage: "Alert rule has been updated.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })

  }

  handleSubmitSuccess = ({ data: { updateCheckAlertRule } }) => {
    const {
      currentWorkspace,
      datastore,
      check,
      history
    } = this.props

    const { errors } = updateCheckAlertRule

    if (!errors) {
      history.push(`/${currentWorkspace.slug}/datastores/${datastore.slug}/checks/${check.pk}`)
    }
  }

  render() {
    const {
      check,
      checkAlertRule,
      datastore,
      form,
      channelOptions,
      intervalOptions,
      hasPermission,
      loading,
      submitting,
    } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Edit Alert Rule - ${datastore.slug} - Metamapper`}
        hideSchemaSelector
      >
        <Row>
          <Col span={22} offset={1}>
            <h2>
              Edit Alert Rule
            </h2>
            <Card className="mt-20">
              <CheckAlertRuleEditForm
                form={form}
                check={check}
                checkAlertRule={checkAlertRule}
                datastore={datastore}
                channelOptions={channelOptions}
                intervalOptions={intervalOptions}
                hasPermission={hasPermission}
                isSubmitting={submitting}
                onSubmit={this.handleSubmit}
              />
            </Card>
          </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ check, datastore }) => {
  return !datastore || !check || !datastore.hasOwnProperty("id") || !check.hasOwnProperty("id")
})

const enhance = compose(
  Form.create(),
  withWriteAccess,
  withGetCheckAlertRuleOptions,
  withGetDatastoreSettings,
  withGetDatastoreCheck,
  withGetCheckAlertRule,
  withLargeLoader,
  withNotFound,
  graphql(UpdateCheckAlertRuleMutation),
  withGraphQLMutation,
)

export default enhance(DatastoreCheckAlertRuleEdit)
