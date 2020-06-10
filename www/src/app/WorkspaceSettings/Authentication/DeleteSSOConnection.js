import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Icon, Popconfirm } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import GetSSOConnections from "graphql/queries/GetSSOConnections"
import RestrictedButton from "app/Common/RestrictedButton"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteSSOConnectionMutation from "graphql/mutations/DeleteSSOConnection"

class DeleteSSOConnection extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { connectionId } = this.props
    const payload = {
      successMessage: "Connection has been removed.",
      variables: {
        id: connectionId,
      },
      refetchQueries: [
        {
          query: GetSSOConnections,
          variables: {},
        },
      ],
    }

    this.props.handleMutation(payload)
  }

  render() {
    const { hasPermission } = this.props
    return (
      <Popconfirm
        title="Are you sure you want to delete this connection?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteSSOConnection.Confirm"
      >
        <RestrictedButton
          type="danger"
          size="small"
          shape="circle"
          hasPermission={hasPermission}
          data-test="DeleteSSOConnection.Submit"
        >
          <Icon type="delete" />
        </RestrictedButton>
      </Popconfirm>
    )
  }
}

DeleteSSOConnection.propTypes = {
  connectionId: PropTypes.string.isRequired,
}

export default compose(
  withSuperUserAccess,
  graphql(DeleteSSOConnectionMutation),
  withGraphQLMutation
)(DeleteSSOConnection)
