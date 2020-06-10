import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { find } from "lodash"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withLoader from "hoc/withLoader"
import SetDefaultSSOConnectionMutation from "graphql/mutations/SetDefaultSSOConnection"
import GetSSOConnections from "graphql/queries/GetSSOConnections"
import SetDefaultSSOConnectionForm from "./SetDefaultSSOConnectionForm"

class SetDefaultSSOConnection extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Default connection has been updated.",
        refetchQueries: [
          {
            query: GetSSOConnections,
            variables: {},
          },
        ],
      }

      this.props.handleMutation(payload)
    })
  }

  render() {
    const { form, ssoConnections, hasPermission, submitting } = this.props

    const defaultConnection = find(ssoConnections, { isDefault: true })
    let defaultConnectionId = null

    if (defaultConnection) {
      defaultConnectionId = defaultConnection.pk
    }

    return (
      <SetDefaultSSOConnectionForm
        form={form}
        defaultConnectionId={defaultConnectionId}
        ssoConnections={ssoConnections}
        hasPermission={hasPermission}
        isSubmitting={submitting}
        onSubmit={this.handleSubmit}
      />
    )
  }
}

const withForm = Form.create()

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

const enhance = compose(
  withSuperUserAccess,
  withForm,
  withLargeLoader,
  graphql(SetDefaultSSOConnectionMutation),
  withGraphQLMutation
)

export default enhance(SetDefaultSSOConnection)
