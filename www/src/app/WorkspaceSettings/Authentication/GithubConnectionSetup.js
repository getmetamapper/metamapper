import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Helmet } from "react-helmet"
import { Form } from "antd"
import { find } from "lodash"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import withGetGithubOrganizations from "graphql/withGetGithubOrganizations"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import CreateSSOConnectionMutation from "graphql/mutations/CreateSSOConnection"
import GithubConnectionSetupForm from "./GithubConnectionSetupForm"

class GithubConnectionSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      ssoConnection: { pk: ssoPrimaryKey, provider },
      githubOrganizations,
    } = this.props

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const { id: ident, login } = find(githubOrganizations, {
        id: variables.entityId,
      })

      const payload = {
        variables: {
          id: ssoPrimaryKey,
          provider: provider.toUpperCase(),
          extras: {
            ident,
            login,
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
    const {
      currentWorkspace,
      form,
      githubOrganizations,
      loading,
      hasPermission,
      submitting,
    } = this.props
    return (
      <>
        <Helmet>
          <title>
            Github Connection Setup - {currentWorkspace.slug} - Metamapper
          </title>
        </Helmet>
        <GithubConnectionSetupForm
          form={form}
          hasPermission={hasPermission}
          githubOrganizations={githubOrganizations}
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
  withGetGithubOrganizations,
  graphql(CreateSSOConnectionMutation),
  withGraphQLMutation
)

export default enhance(GithubConnectionSetup)
