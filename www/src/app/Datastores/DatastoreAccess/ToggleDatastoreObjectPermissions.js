import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Switch } from "antd"
import ToggleDatastoreObjectPermissionsMutation from "graphql/mutations/ToggleDatastoreObjectPermissions"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class ToggleDatastoreObjectPermissions extends Component {
  handleChange = () => {
    const {
      datastore: { id },
    } = this.props

    const payload = {
      variables: { id },
      successMessage: null,
    }

    this.props.onStartChange()
    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    const { isEnabled, errors } = data.toggleDatastoreObjectPermissions

    if (!errors || errors.length <= 0) {
      this.props.onFinishChange(isEnabled)
    } else {
      this.props.onFinishChange(false)
    }
  }

  render() {
    const { isEnabled, hasPermission } = this.props
    return (
      <div style={{ display: 'table', width: '100%' }}>
        <div style={{ display: 'table-row' }}>
          <div style={{ display: 'table-cell', width: 56 }}>
            <Switch
              defaultChecked={isEnabled}
              onChange={this.handleChange}
              disabled={!hasPermission}
              data-test="ToggleDatastoreObjectPermissions"
            />
          </div>
          <div style={{ display: 'table-cell' }}>
            <b>Limit access to this connection.</b>
            <p className="mb-0">
              Owners have access to limited connections by default. Manage other user and group access below.
            </p>
          </div>
        </div>
      </div>
    )
  }
}

const enhance = compose(
  graphql(ToggleDatastoreObjectPermissionsMutation),
  withGraphQLMutation
)

export default enhance(ToggleDatastoreObjectPermissions)
