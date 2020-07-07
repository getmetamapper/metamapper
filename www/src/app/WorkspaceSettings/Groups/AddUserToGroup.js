import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form } from "antd"
import AddUserToGroupForm from "app/WorkspaceSettings/Groups/AddUserToGroupForm"
import AddUserToGroupMutation from "graphql/mutations/AddUserToGroup"
import GetWorkspaceGroups from "graphql/queries/GetWorkspaceGroups"
import GetWorkspaceGroupUsers from "graphql/queries/GetWorkspaceGroupUsers"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class AddUserToGroup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, { userId }) => {
      if (err || !userId) return

      const {
        group: { id: groupId },
      } = this.props

      const payload = {
        variables: { groupId, userId },
        successMessage: "User has been added to the group.",
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
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.addUserToGroup

    if (!errors || errors.length <= 0 ) {
      this.props.form.resetFields()
    }
  }

  render() {
    const { form, users, hasPermission, submitting } = this.props
    return (
      <AddUserToGroupForm
        form={form}
        users={users}
        hasPermission={hasPermission}
        onSubmit={this.handleSubmit}
        isSubmitting={submitting}
      />
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  graphql(AddUserToGroupMutation),
  withGraphQLMutation
)

export default enhance(AddUserToGroup)
