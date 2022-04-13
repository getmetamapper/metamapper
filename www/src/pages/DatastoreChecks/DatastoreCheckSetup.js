import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import DatastoreCheckSetupForm from "app/Datastores/DatastoreChecks/CheckSetup/CheckSetupForm"
import CreateCheckMutation from "graphql/mutations/CreateCheck"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreCheckSetup extends Component {
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
        label: "Checks",
        to: `/${slug}/datastores/${datastoreSlug}/checks`,
      },
      {
        label: "New Check"
      },
    ]
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const { datastore: { id: datastoreId } } = this.props

      const payload = {
        variables: {
          datastoreId,
          ...variables,
        },
        successMessage: "Check has been created.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data: { createCheck } }) => {
    const {
      currentWorkspace,
      datastore,
      history
    } = this.props

    const { check, errors } = createCheck

    if (!errors) {
      history.push(`/${currentWorkspace.slug}/datastores/${datastore.slug}/checks/${check.pk}`)
    }
  }

  render() {
    const {
      datastore,
      form,
      hasPermission,
      loading,
      submitting,
    } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`New Check - ${datastore.slug} - Metamapper`}
        hideSchemaSelector
      >
        <DatastoreCheckSetupForm
          form={form}
          hasPermission={hasPermission}
          isSubmitting={submitting}
          onSubmit={this.handleSubmit}
        />
      </DatastoreLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

const enhance = compose(
  Form.create(),
  withWriteAccess,
  withGetDatastoreSettings,
  withLargeLoader,
  withNotFound,
  graphql(CreateCheckMutation),
  withGraphQLMutation,
)

export default enhance(DatastoreCheckSetup)
