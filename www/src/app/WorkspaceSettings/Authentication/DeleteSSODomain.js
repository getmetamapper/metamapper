import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Popconfirm } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import GetSSODomains from "graphql/queries/GetSSODomains"
import RestrictedButton from "app/Common/RestrictedButton"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteSSODomainMutation from "graphql/mutations/DeleteSSODomain"

class DeleteSSODomain extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { domainID } = this.props
    const payload = {
      successMessage: "Domain has been removed.",
      variables: {
        id: domainID,
      },
      refetchQueries: [
        {
          query: GetSSODomains,
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
        title="Are you sure you want to delete this domain?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteSSODomain.Confirm"
      >
        <RestrictedButton
          type="danger"
          hasPermission={hasPermission}
          data-test="DeleteSSODomain.Submit"
        >
          Remove
        </RestrictedButton>
      </Popconfirm>
    )
  }
}

DeleteSSODomain.propTypes = {
  domainID: PropTypes.string.isRequired,
}

export default compose(
  withSuperUserAccess,
  graphql(DeleteSSODomainMutation),
  withGraphQLMutation
)(DeleteSSODomain)
