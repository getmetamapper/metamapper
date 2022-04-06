import React, { Component } from "react"
import { Button, Divider } from "antd"
import { compose } from "react-apollo"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import ApiTokensTable from "app/WorkspaceSettings/Api/ApiTokensTable"
import ApiTokenSetup from "app/WorkspaceSettings/Api/ApiTokenSetup"
import ApiTokenPreview from "app/WorkspaceSettings/Api/ApiTokenPreview"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetApiTokens from "graphql/withGetApiTokens"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

const breadcrumbs = ({ slug }) => {
  return [
    {
      label: "Home",
      to: `/${slug}/datastores`,
    },
    {
      label: "Workspace Settings",
      to: `/${slug}/settings`,
    },
    {
      label: "API",
      to: `/${slug}/settings/api`,
    },
  ]
}


class Api extends Component {
  constructor(props) {
    super(props)

    this.state = {
      tokenName: null,
      tokenSecret: null,
      setupVisible: false,
    }

    this.handleSetupSuccess = this.handleSetupSuccess.bind(this)
  }

  onOpenSetupForm = () => {
    this.setState({ setupVisible: true })
  }

  onCloseSetupForm = () => {
    this.setState({ setupVisible: false })
  }

  handleSetupSuccess = (tokenName, tokenSecret) => {
    this.setState({
      setupVisible: false,
      tokenName,
      tokenSecret,
    })
  }

  render() {
    const {
      apiTokens,
      hasPermission,
      workspace,
      loading,
    } = this.props
    const {
      tokenName,
      tokenSecret,
      setupVisible,
    } = this.state
    return (
      <WorkspaceLayout
        title={`API - ${workspace.slug} - Metamapper`}
        breadcrumbs={breadcrumbs}
      >
        <h2>API</h2>
        <Divider />
        <div className="api-tokens">
          {tokenSecret && (
            <ApiTokenPreview
              tokenName={tokenName}
              tokenSecret={tokenSecret}
              onClose={() => this.setState({ tokenName: null, tokenSecret: null })}
            />
          )}
          <h3>Access Tokens</h3>
          <p>
            Access tokens allow for authentication when using the Metamapper API.
          </p>
          {hasPermission && (
            <div className="api-token-setup-btn">
              <Button type="primary" onClick={this.onOpenSetupForm}>
                Create Access Token
              </Button>
            </div>
          )}
          <ApiTokensTable
            apiTokens={apiTokens}
            loading={loading}
          />
        </div>
        <>
          <ApiTokenSetup
            visible={setupVisible}
            onCancel={this.onCloseSetupForm}
            onSuccess={this.handleSetupSuccess}
          />
        </>
      </WorkspaceLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace || !workspace.hasOwnProperty("id")
})

export default compose(
  withGetWorkspaceBySlug,
  withGetApiTokens,
  withSuperUserAccess,
  withLargeLoader,
  withNotFound,
)(Api)
