import React from "react"
import { compose } from "react-apollo"
import { Button, Divider } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import Link from "app/Navigation/Link"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import SSOConnectionsTable from "app/WorkspaceSettings/Authentication/SSOConnectionsTable"
import SSODomainsTable from "app/WorkspaceSettings/Authentication/SSODomainsTable"
import SSODomainSetup from "app/WorkspaceSettings/Authentication/SSODomainSetup"
import SetDefaultSSOConnection from "app/WorkspaceSettings/Authentication/SetDefaultSSOConnection"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetSSOConnections from "graphql/withGetSSOConnections"
import withGetSSODomains from "graphql/withGetSSODomains"
import withGetSSOProviders from "graphql/withGetSSOProviders"

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
      label: "Authentication",
      to: `/${slug}/settings/authentication`,
    },
  ]
}

const Authentication = ({
  workspace,
  loading,
  hasPermission,
  ssoProviders,
  ssoConnections,
  ssoDomains,
}) => (
  <WorkspaceLayout
    title={`Authentication - ${workspace.slug} - Metamapper`}
    breadcrumbs={breadcrumbs}
  >
    <h2>Authentication</h2>
    <Divider />
    <div className="sso-connections">
      <h3>Connections</h3>
      <p>
        Single Sign-On (or SSO) connections allow you to manage workspace
        membership via a third-party provider.
      </p>
      {hasPermission && (
        <div className="add-sso-connection-btn">
          <Link to="/settings/authentication/setup">
            <Button type="primary">Add New Connection</Button>
          </Link>
        </div>
      )}
      <SSOConnectionsTable
        ssoConnections={ssoConnections}
        ssoProviders={ssoProviders}
        loading={loading}
      />
    </div>
    <Divider />
    <div className="sso-domains">
      <h3>Domains</h3>
      <p>
        This section contains domains that are owned by your workspace. Once
        verified, these domains can be used to enforce automatic Single Sign On
        for your users.
      </p>
      <div className="sso-domain-setup">
        <SSODomainSetup />
      </div>
      <SSODomainsTable ssoDomains={ssoDomains} loading={loading} />
    </div>
    <Divider />
    <div className="sso-connections">
      <h3>Default Connection</h3>
      <p>
        If your workspace has verified domains, you can set a default connection
        to redirect your users automatically when they log in.
      </p>
      <p>This can baccessed by this link:</p>
      <SetDefaultSSOConnection
        ssoConnections={ssoConnections}
        loading={loading}
      />
    </div>
  </WorkspaceLayout>
)

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace || !workspace.hasOwnProperty("id")
})

export default compose(
  withSuperUserAccess,
  withGetWorkspaceBySlug,
  withGetSSOProviders,
  withGetSSOConnections,
  withGetSSODomains,
  withLargeLoader,
  withNotFound,
)(Authentication)
