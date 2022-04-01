import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Icon, Tooltip, Switch } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import GetApiTokens from "graphql/queries/GetApiTokens"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import EnableApiTokenMutation from "graphql/mutations/EnableApiToken"

class EnableApiToken extends Component {
  constructor(props) {
    super(props)

    this.handleToggle = this.handleToggle.bind(this)
  }

  handleToggle(isEnabled) {
    const { tokenId } = this.props
    const payload = {
      successMessage: null,
      variables: {
        id: tokenId,
        isEnabled,
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
    const { isEnabled, hasPermission } = this.props
    return (
      <Tooltip title={isEnabled ? "Click to disable" : "Click to enable"}>
        <Switch
          checkedChildren={<Icon type="check" />}
          unCheckedChildren={<Icon type="close" />}
          defaultChecked={isEnabled}
          disabled={!hasPermission}
          onChange={this.handleToggle}
          data-test="EnableApiToken.Submit"
        />
      </Tooltip>
    )
  }
}

EnableApiToken.propTypes = {
  tokenId: PropTypes.string.isRequired,
  isEnabled: PropTypes.bool.isRequired,
}

export default compose(
  withSuperUserAccess,
  graphql(EnableApiTokenMutation),
  withGraphQLMutation
)(EnableApiToken)
