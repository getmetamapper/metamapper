import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Col, Form, Row } from "antd"
import { Helmet } from "react-helmet"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import DatastoreSetupForm from "app/Datastores/DatastoreSetupForm"
import CreateDatastoreMutation from "graphql/mutations/CreateDatastore"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreSetup extends Component {
  state = {}

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Datastore has been created.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { currentWorkspace, history } = this.props
    const { datastore, errors } = data.createDatastore

    if (!errors) {
      history.push(`/${currentWorkspace.slug}/datastores/${datastore.slug}`)
    }
  }

  render() {
    const { currentWorkspace, form, hasPermission, submitting } = this.props
    return (
      <Row>
        <Helmet>
          <title>Datastore Setup - {currentWorkspace.slug} - Metamapper</title>
        </Helmet>
        <Col span={12} offset={6}>
          <DatastoreSetupForm
            form={form}
            hasPermission={hasPermission}
            isSubmitting={submitting}
            onSubmit={this.handleSubmit}
          />
        </Col>
      </Row>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withWriteAccess,
  graphql(CreateDatastoreMutation),
  withGraphQLMutation
)

export default enhance(DatastoreSetup)
