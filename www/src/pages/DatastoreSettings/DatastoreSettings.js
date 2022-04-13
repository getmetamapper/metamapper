import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Card, Col, Divider, Form, Row } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import DeleteDatastore from "app/Datastores/DeleteDatastore"
import DatastoreSettingsForm from "app/Datastores/DatastoreSettings/DatastoreSettingsForm"
import AllowedCustomPropertySettings from "app/Datastores/DatastoreSettings/AllowedCustomPropertySettings"
import UpdateDatastoreMetadataMutation from "graphql/mutations/UpdateDatastoreMetadata"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class DatastoreSettings extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs(datastore) {
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
        label: "Settings",
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
        successMessage: "Datastore has been updated.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { datastore, errors } = data.updateDatastoreMetadata
    const {
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    if (datastore && !errors) {
      const {
        history,
        currentWorkspace: { slug: workspaceSlug },
      } = this.props

      if (datastore.slug !== datastoreSlug) {
        history.push(`/${workspaceSlug}/datastores/${datastore.slug}/settings`)
      }
    }
  }

  render() {
    const { datastore, form, hasPermission, loading, submitting } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Datastore Settings - ${datastore.slug} - Metamapper`}
      >
        <Row className="datastore-settings-container">
          <Col span={16} offset={4}>
            <Card className="datastore-settings">
              <div className="datastore-settings-header">
                <h3>Datastore Settings</h3>
                <Divider />
              </div>
              <DatastoreSettingsForm
                datastore={datastore}
                form={form}
                hasPermission={hasPermission}
                isSubmitting={submitting}
                onSubmit={this.handleSubmit}
              />
              {hasPermission && (
                <div className="datastore-deletion">
                  <DeleteDatastore datastore={datastore} />
                </div>
              )}
            </Card>
            <Card className="custom-properties-settings">
              <div className="custom-properties-settings-header">
                <h3>Allowed Custom Properties</h3>
                <Divider />
              </div>
              <AllowedCustomPropertySettings
                datastore={datastore}
                hasPermission={hasPermission}
              />
            </Card>
          </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

const withForm = Form.create()

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

const enhance = compose(
  withForm,
  withRouter,
  withWriteAccess,
  withGetDatastoreSettings,
  graphql(UpdateDatastoreMetadataMutation),
  withGraphQLMutation,
  withLargeLoader,
  withNotFound,
)

export default enhance(DatastoreSettings)
