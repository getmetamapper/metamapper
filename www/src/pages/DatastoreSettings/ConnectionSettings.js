import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Card, Col, Divider, Form, Row } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import ConnectionSettingsForm from "app/Datastores/ConnectionSettings/ConnectionSettingsForm"
import UpdateDatastoreJdbcConnectionMutation from "graphql/mutations/UpdateDatastoreJdbcConnection"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withNotFoundHandler from "hoc/withNotFoundHandler"

class ConnectionSettings extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs = (datastore) => {
    const {
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
        label: "Connection",
      },
    ]
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { id } = this.props.datastore

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: { id, ...variables },
        successMessage: "Connection has been updated.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { form } = this.props
    const { errors } = data.updateDatastoreJdbcConnection

    if (!errors) {
      form.setFieldsValue({ password: "" })
    }
  }

  render() {
    const { datastore, form, hasPermission, loading, submitting } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Connection Settings - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={16} offset={4}>
            <Card>
              <h3>Connection Settings</h3>
              <Divider />
              <ConnectionSettingsForm
                datastore={datastore}
                form={form}
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

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

const withForm = Form.create()

const enhance = compose(
  withForm,
  withWriteAccess,
  withGetDatastoreSettings,
  graphql(UpdateDatastoreJdbcConnectionMutation),
  withGraphQLMutation,
  withLargeLoader,
  withNotFound,
)

export default enhance(ConnectionSettings)
