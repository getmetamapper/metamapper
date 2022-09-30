import React from "react"
import { Divider } from "antd"
import { compose } from "react-apollo"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import IntegrationsTable from "app/WorkspaceSettings/Integrations/IntegrationsTable"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetAvailableIntegrations from "graphql/withGetAvailableIntegrations"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"

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
      label: "Integrations",
      to: `/${slug}/settings/integrations`,
    },
  ]
}

const Integrations = ({ workspace, availableIntegrations, loading }) => (
  <WorkspaceLayout
    title={`Integrations - ${workspace.slug} - Metamapper`}
    breadcrumbs={breadcrumbs}
  >
    <h2>Integrations</h2>
    <Divider />
    <IntegrationsTable integrations={availableIntegrations} />
  </WorkspaceLayout>
)

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace
})

export default compose(
  withGetWorkspaceBySlug,
  withGetAvailableIntegrations,
  withLargeLoader,
  withNotFound,
)(Integrations)
