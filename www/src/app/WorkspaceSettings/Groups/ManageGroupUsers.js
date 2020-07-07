import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import AddUserToGroup from "app/WorkspaceSettings/Groups/AddUserToGroup"
import ManageGroupUsersTable from "app/WorkspaceSettings/Groups/ManageGroupUsersTable"
import GetWorkspaceGroupUsers from "graphql/queries/GetWorkspaceGroupUsers"
import GetWorkspaceGroups from "graphql/queries/GetWorkspaceGroups"
import RemoveUserFromGroupMutation from "graphql/mutations/RemoveUserFromGroup"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetWorkspaceUsers from "graphql/withGetWorkspaceUsers"

class ManageGroupUsers extends Component {
  handleRemoveUser = ({ id: userId }) => {
    const {
      group: { id: groupId },
    } = this.props

    const payload = {
      variables: { groupId, userId },
      successMessage: "User has been removed from the group.",
      refetchQueries: [
        {
          query: GetWorkspaceGroups,
        },
        {
          query: GetWorkspaceGroupUsers,
          variables: { groupId },
        },
      ],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.removeUserFromGroup

    if (!errors || errors.length <= 0 ) {
      this.props.form.resetFields()
    }
  }

  render() {
    const {
      form,
      group,
      workspaceUsers,
      hasPermission,
      submitting,
      visible,
      onCancel,
    } = this.props
    return (
      <Modal
        title="Manage Group Users"
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        {hasPermission && (
          <AddUserToGroup
            group={group}
            users={workspaceUsers}
            form={form}
            hasPermission={hasPermission}
            onSubmit={this.handleSubmit}
            isSubmitting={submitting}
          />
        )}
        <ManageGroupUsersTable
          group={group}
          hasPermission={hasPermission}
          onRemove={this.handleRemoveUser}
        />
      </Modal>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withSuperUserAccess,
  withGetWorkspaceUsers,
  graphql(RemoveUserFromGroupMutation),
  withGraphQLMutation
)

export default enhance(ManageGroupUsers)
