import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import { withUserContext } from "context/UserContext"
import { withLargeLoader } from "hoc/withLoader"
import GrantDatastoreUserAccessForm from "./GrantDatastoreAccessForm"
import GetDatastoreAccessPrivileges from "graphql/queries/GetDatastoreAccessPrivileges"
import UpdateDatastoreAccessPrivilegesMutation from "graphql/mutations/UpdateDatastoreAccessPrivileges"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetWorkspaceUsers from "graphql/withGetWorkspaceUsers"

class GrantDatastoreUserAccess extends Component {
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
      workspaceUsers,
      visible,
    } = this.props
    return (
      <Modal
        title="Grant User Access To Datastore"
        visible={visible}
        onCancel={this.handleCancel}
        footer={null}
      >
        <GrantDatastoreUserAccessForm
          form={form}
          objectLabel="Choose a Team Member"
          objectLookup="userId"
          objects={workspaceUsers}
          testLabel="GrantDatastoreUserAccessForm"
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
  withGetWorkspaceUsers,
  graphql(UpdateDatastoreAccessPrivilegesMutation),
  withGraphQLMutation,
  withLargeLoader,
)

export default enhance(GrantDatastoreUserAccess)
