import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form, message } from "antd"
import { withOwnersOnly } from "hoc/withPermissionsRequired"
import GetWorkspaceUsers from "graphql/queries/GetWorkspaceUsers"
import GrantMembershipMutation from "graphql/mutations/GrantMembership"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import InviteUserToWorkspaceForm from "./InviteUserToWorkspaceForm"

class InviteUserToTeam extends Component {
  handleUserInvited = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      if (!variables.email) {
        message.error("Please provide a valid email.")
        return
      }

      const { workspace } = this.props
      const payload = {
        successMessage: "User has been invited.",
        variables,
        refetchQueries: [
          {
            query: GetWorkspaceUsers,
            variables: {
              workspaceId: workspace.id,
              activeOnly: false,
            },
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = (payload) => {
    this.props.form.resetFields()
  }

  render() {
    const { form, hasPermission, submitting } = this.props
    return (
      <div className="invite-user-to-workspace">
        <InviteUserToWorkspaceForm
          form={form}
          hasPermission={hasPermission}
          isSubmitting={submitting}
          onSubmit={this.handleUserInvited}
        />
      </div>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withOwnersOnly,
  graphql(GrantMembershipMutation),
  withGraphQLMutation
)

export default enhance(InviteUserToTeam)
