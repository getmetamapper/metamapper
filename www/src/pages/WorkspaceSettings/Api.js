import React, { Component } from "react"
import { Alert, Button, Divider } from "antd"
import { compose } from "react-apollo"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import ApiTokensTable from "app/WorkspaceSettings/Api/ApiTokensTable"
import ApiTokenSetup from "app/WorkspaceSettings/Api/ApiTokenSetup"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetApiTokens from "graphql/withGetApiTokens"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import CopyInput from "app/Common/CopyInput"

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
            <div className="api-token-setup-secret">
              <Alert
                type="success"
                closable
                message={<span>API token <b>{tokenName}</b> has been created.</span>}
                description={
                  <div className="api-token-setup-secret-inner">
                    <p>
                      Make sure to copy the access token now. You won’t be able to see it again!
                    </p>
                    <CopyInput value={tokenSecret} />
                   </div>
                }
                onClose={() => this.setState({ tokenName: null, tokenSecret: null })}
              />
            </div>
          )}
          {hasPermission && (
            <div className="api-token-setup-btn">
              <Button type="primary" onClick={this.onOpenSetupForm}>
                Create API Token
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
