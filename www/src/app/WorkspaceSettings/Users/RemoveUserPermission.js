import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Button, Icon, Tooltip, Popconfirm } from "antd"
import { withUserContext } from "context/UserContext"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import GetWorkspaceUsers from "graphql/queries/GetWorkspaceUsers"
import RevokeMembershipMutation from "graphql/mutations/RevokeMembership"
import RestrictedButton from "app/Common/RestrictedButton"

class RemoveUserPermission extends Component {
  handleRevokeMembership = (evt) => {
    evt.preventDefault()

    const { email, workspace } = this.props

    const payload = {
      successMessage: "User has been removed.",
      variables: {
        email,
      },
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
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.revokeMembership
    const { currentUser, email } = this.props

    if (!errors && currentUser.email === email) {
      window.location.href = '/workspaces'
    }
  }

  renderLeaveButton = () => {
    const { isLastOwner } = this.props
    return (
      <Tooltip
        title={
          isLastOwner
            ? "You cannot leave this workspace as you are the only owner."
            : null
        }
      >
        <Button type="default" disabled={isLastOwner}>
          <Icon type="logout" /> Leave
        </Button>
      </Tooltip>
    )
  }

  renderRemovalButton = () => {
    const { hasPermission, submitting } = this.props
    return (
      <RestrictedButton type="danger" hasPermission={hasPermission}>
        <Icon type={submitting ? "loading" : "close-circle"} /> Remove
      </RestrictedButton>
    )
  }

  render() {
    const { currentUser, email } = this.props
    return (
      <>
        <Popconfirm
          title="Are you sure?"
          onConfirm={this.handleRevokeMembership}
          okText="Yes"
          cancelText="No"
        >
          {currentUser.email === email
            ? this.renderLeaveButton()
            : this.renderRemovalButton()}
        </Popconfirm>
      </>
    )
  }
}

const enhance = compose(
  withUserContext,
  graphql(RevokeMembershipMutation),
  withGraphQLMutation
)

export default enhance(RemoveUserPermission)
