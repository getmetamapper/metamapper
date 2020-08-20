import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetSSOProviders from "graphql/withGetSSOProviders"
import UpdateSSOConnectionMutation from "graphql/mutations/UpdateSSOConnection"
import SamlConnectionSetupForm from "./SamlConnectionSetupForm"

class UpdateSamlConnection extends Component {
  componentWillMount() {
    const {
      currentWorkspace: { slug: workspaceSlug },
      ssoConnection: { protocol },
    } = this.props

    if (protocol && protocol !== "saml2") {
      this.props.history.push(`/${workspaceSlug}/settings/authentication`)
    }
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      ssoConnection: { id },
    } = this.props

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: {
          id,
          ...variables,
        },
        successMessage: `Connection has been updated.`,
      }

      this.props.handleMutation(payload)
    })
  }

  render() {
    const { form, hasPermission, ssoConnection, submitting } = this.props
    return (
      <SamlConnectionSetupForm
        form={form}
        ssoConnection={ssoConnection}
        hasPermission={hasPermission}
        isEditing
        isSubmitting={submitting}
        onSubmit={this.handleSubmit}
      />
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withRouter,
  withUserContext,
  withWriteAccess,
  withGetSSOProviders,
  withLargeLoader,
  graphql(UpdateSSOConnectionMutation),
  withGraphQLMutation
)

export default enhance(UpdateSamlConnection)
