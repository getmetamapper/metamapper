import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Icon, Popconfirm } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import GetApiTokens from "graphql/queries/GetApiTokens"
import RestrictedButton from "app/Common/RestrictedButton"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteApiTokenMutation from "graphql/mutations/DeleteApiToken"

class DeleteApiToken extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { tokenId } = this.props
    const payload = {
      successMessage: null,
      variables: {
        id: tokenId,
      },
      refetchQueries: [
        {
          query: GetApiTokens,
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
        title="Are you sure you want to delete this API token?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteApiToken.Confirm"
      >
        <RestrictedButton
          type="danger"
          size="small"
          shape="circle"
          hasPermission={hasPermission}
          data-test="DeleteApiToken.Submit"
        >
          <Icon type="delete" />
        </RestrictedButton>
      </Popconfirm>
    )
  }
}

DeleteApiToken.propTypes = {
  tokenId: PropTypes.string.isRequired,
}

export default compose(
  withSuperUserAccess,
  graphql(DeleteApiTokenMutation),
  withGraphQLMutation
)(DeleteApiToken)
