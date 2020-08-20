import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Helmet } from "react-helmet"
import { Form } from "antd"
import { find } from "lodash"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetSSOProviders from "graphql/withGetSSOProviders"
import CreateSSOConnectionMutation from "graphql/mutations/CreateSSOConnection"
import SamlConnectionSetupForm from "./SamlConnectionSetupForm"

class SamlConnectionSetup extends Component {
  componentDidMount() {
    const {
      currentWorkspace: { slug: workspaceSlug },
      history,
      ssoConnection: { provider },
      ssoProviders,
    } = this.props

    if (!find(ssoProviders, { provider: provider.toUpperCase() })) {
      history.push(`/${workspaceSlug}/settings/authentication/setup`)
    }
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      ssoConnection: { pk: ssoPrimaryKey, provider },
    } = this.props

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: {
          id: ssoPrimaryKey,
          provider: provider.toUpperCase(),
          ...variables,
        },
        successMessage: "Connection has been created.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data: { createSSOConnection } }) => {
    const { errors } = createSSOConnection
    const {
      currentWorkspace: { slug: workspaceSlug },
    } = this.props

    if (!errors) {
      this.props.history.push(`/${workspaceSlug}/settings/authentication`)
    }
  }

  render() {
    const {
      currentWorkspace,
      form,
      hasPermission,
      ssoConnection,
      submitting,
      match: {
        params: { provider },
      },
    } = this.props
    return (
      <>
        <Helmet>
          <title>
            SAML Connection Setup - {currentWorkspace.slug} - Metamapper
          </title>
        </Helmet>
        <SamlConnectionSetupForm
          form={form}
          provider={provider}
          ssoConnection={ssoConnection}
          hasPermission={hasPermission}
          isEditing={false}
          isSubmitting={submitting}
          onSubmit={this.handleSubmit}
        />
      </>
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
  graphql(CreateSSOConnectionMutation),
  withGraphQLMutation
)

export default enhance(SamlConnectionSetup)
