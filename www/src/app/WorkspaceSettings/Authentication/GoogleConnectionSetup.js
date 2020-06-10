import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Helmet } from "react-helmet"
import { Form } from "antd"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import qs from "query-string"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import CreateSSOConnectionMutation from "graphql/mutations/CreateSSOConnection"
import GoogleConnectionSetupForm from "./GoogleConnectionSetupForm"

class GoogleConnectionSetup extends Component {
  constructor(props) {
    super(props)

    const { domain } = qs.parse(window.location.search)

    this.state = {
      domain,
    }
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      ssoConnection: { pk: ssoPrimaryKey, provider },
    } = this.props

    const { domain } = this.state

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: {
          id: ssoPrimaryKey,
          provider: provider.toUpperCase(),
          extras: {
            domain,
          },
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
    const { domain } = this.state
    const {
      currentWorkspace,
      form,
      loading,
      hasPermission,
      submitting,
    } = this.props
    return (
      <>
        <Helmet>
          <title>
            Google Connection Setup - {currentWorkspace.slug} - Metamapper
          </title>
        </Helmet>
        <GoogleConnectionSetupForm
          form={form}
          hasPermission={hasPermission}
          domain={domain}
          loading={loading}
          isSubmitting={submitting}
          onSubmit={this.handleSubmit}
        />
      </>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withWriteAccess,
  withForm,
  withRouter,
  graphql(CreateSSOConnectionMutation),
  withGraphQLMutation
)

export default enhance(GoogleConnectionSetup)
