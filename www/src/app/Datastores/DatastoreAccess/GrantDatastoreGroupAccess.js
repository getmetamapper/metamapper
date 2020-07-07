import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import { withUserContext } from "context/UserContext"
import { withLargeLoader } from "hoc/withLoader"
import GrantDatastoreGroupAccessForm from "./GrantDatastoreAccessForm"
import GetDatastoreAccessPrivileges from "graphql/queries/GetDatastoreAccessPrivileges"
import UpdateDatastoreAccessPrivilegesMutation from "graphql/mutations/UpdateDatastoreAccessPrivileges"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetWorkspaceGroups from "graphql/withGetWorkspaceGroups"

class GrantDatastoreGroupAccess extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        datastore: { id },
      } = this.props

      const payload = {
        successMessage: "Changes have been saved.",
        variables: { id, ...variables },
        refetchQueries: [
          {
            query: GetDatastoreAccessPrivileges,
            variables: {
              datastoreId: id,
            },
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    this.props.form.setFieldsValue({objectId: ''})
  }

  handleCancel = () => {
    this.props.onCancel()
    this.props.form.resetFields()
  }

  render() {
    const {
      form,
      submitting,
      workspaceGroups,
      visible,
    } = this.props
    return (
      <Modal
        title="Grant Group Access To Datastore"
        visible={visible}
        onCancel={this.handleCancel}
        footer={null}
      >
        <GrantDatastoreGroupAccessForm
          form={form}
          objectLabel="Choose a Group"
          objects={workspaceGroups}
          testLabel="GrantDatastoreGroupAccessForm"
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
        />
      </Modal>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withUserContext,
  withGetWorkspaceGroups,
  graphql(UpdateDatastoreAccessPrivilegesMutation),
  withGraphQLMutation,
  withLargeLoader,
)

export default enhance(GrantDatastoreGroupAccess)
