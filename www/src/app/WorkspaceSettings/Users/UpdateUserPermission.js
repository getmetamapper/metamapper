import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Button, Icon, Tag, Select } from "antd"
import { PERMISSION_CHOICES } from "lib/constants"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import GetWorkspaceUsers from "graphql/queries/GetWorkspaceUsers"
import GrantMembershipMutation from "graphql/mutations/GrantMembership"

class UpdateUserPermission extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isEditing: false,
      permissions: props.permissions,
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.email !== this.props.email) {
      this.setState({
        permissions: nextProps.permissions,
      })
    }
  }

  openEditable = () => {
    const { hasPermission } = this.props

    if (hasPermission) {
      this.setState({ isEditing: true })
    }
  }

  closeEditable = () => {
    this.setState({ isEditing: false })
  }

  handleChange = (permissions) => {
    this.setState({ permissions })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { email, workspace } = this.props
    const { permissions } = this.state

    const payload = {
      successMessage: "Membership has been updated.",
      variables: {
        email,
        permissions,
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
    const { errors } = data.grantMembership

    if (!errors) {
      this.setState({ isEditing: false })
    }
  }

  render() {
    const { hasPermission, submitting } = this.props
    const { isEditing, permissions } = this.state
    return (
      <>
        {isEditing ? (
          <div className="update-user-permissions">
            <Select
              defaultValue={PERMISSION_CHOICES[permissions]}
              onChange={this.handleChange}
            >
              {Object.keys(PERMISSION_CHOICES).map((key) => (
                <Select.Option key={key} value={key}>
                  {PERMISSION_CHOICES[key]}
                </Select.Option>
              ))}
            </Select>
            <Button
              type="primary"
              onClick={this.handleSubmit}
              disabled={submitting}
            >
              <Icon type={submitting ? "loading" : "check"} />
            </Button>
            <Button type="default" onClick={this.closeEditable}>
              <Icon type="close" />
            </Button>
          </div>
        ) : (
          <Tag
            className={hasPermission ? "editable" : ""}
            onClick={this.openEditable}
          >
            {PERMISSION_CHOICES[permissions]}
          </Tag>
        )}
      </>
    )
  }
}

const enhance = compose(graphql(GrantMembershipMutation), withGraphQLMutation)

export default enhance(UpdateUserPermission)
