import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Popconfirm, Icon } from "antd"
import DeleteAssetOwnerMutation from "graphql/mutations/DeleteAssetOwner"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteAssetOwner extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
    this.state = {}
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { ownerId, refetchQueries } = this.props
    const payload = {
      successMessage: "Owner has been removed.",
      variables: { id: ownerId },
      refetchQueries: refetchQueries,
    }

    this.props.handleMutation(payload)
  }

  render() {
    const { submitting } = this.props
    return (
      <Popconfirm
        title="Are you sure you want to remove this owner?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteAssetOwner.Confirm"
      >
        <span className="asset-owner-delete" data-test="DeleteAssetOwner.Submit">
          <Icon type={submitting ? 'loading' : 'delete'} />
        </span>
      </Popconfirm>
    )
  }
}

export default compose(
  graphql(DeleteAssetOwnerMutation),
  withGraphQLMutation,
)(DeleteAssetOwner)
