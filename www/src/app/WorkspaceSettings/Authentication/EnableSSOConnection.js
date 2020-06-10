import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Icon, Tooltip, Switch } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import GetSSOConnections from "graphql/queries/GetSSOConnections"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import EnableSSOConnectionMutation from "graphql/mutations/EnableSSOConnection"

class EnableSSOConnection extends Component {
  constructor(props) {
    super(props)

    this.handleToggle = this.handleToggle.bind(this)
  }

  handleToggle(isEnabled) {
    const { connectionId } = this.props
    const payload = {
      successMessage: null,
      variables: {
        id: connectionId,
        isEnabled,
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
    const { isEnabled, hasPermission } = this.props
    return (
      <Tooltip title={isEnabled ? "Click to disable" : "Click to enable"}>
        <Switch
          checkedChildren={<Icon type="check" />}
          unCheckedChildren={<Icon type="close" />}
          defaultChecked={isEnabled}
          disabled={!hasPermission}
          onChange={this.handleToggle}
          style={{ marginRight: 10 }}
          data-test="EnableSSOConnection.Submit"
        />
      </Tooltip>
    )
  }
}

EnableSSOConnection.propTypes = {
  connectionId: PropTypes.string.isRequired,
  isEnabled: PropTypes.bool.isRequired,
}

export default compose(
  withSuperUserAccess,
  graphql(EnableSSOConnectionMutation),
  withGraphQLMutation
)(EnableSSOConnection)
