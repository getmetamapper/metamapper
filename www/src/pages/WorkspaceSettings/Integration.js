import React, { useState } from "react"
import { Divider } from "antd"
import { compose } from "react-apollo"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetIntegrationConfigs from "graphql/withGetIntegrationConfigs"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import RestrictedButton from "app/Common/RestrictedButton"
import IntegrationConfigsTable from "app/WorkspaceSettings/Integrations/IntegrationConfigsTable"
import IntegrationInfo from "app/WorkspaceSettings/Integrations/IntegrationInfo"
import IntegrationConfigSetup from "app/WorkspaceSettings/Integrations/IntegrationConfigSetup"

const breadcrumbs = (integration) => (({ slug }) => {
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
    {
      label: integration.name,
      to: `/${slug}/settings/integrations/${integration.handler}`,
    },
  ]
})

const Integration = ({
  integration,
  integrationConfigs,
  workspace,
  loading,
  hasPermission,
}) => {
  const [setupVisiblity, setSetupVisibility] = useState(false)
  return (
    <WorkspaceLayout
      title={`${integration.name} - Integrations - ${workspace.slug} - Metamapper`}
      breadcrumbs={breadcrumbs(integration)}
    >
      <IntegrationInfo
        avatarSize={80}
        titleSize={20}
        integration={integration}
        showTags
      />
      <Divider />
      <RestrictedButton
        type="primary"
        hasPermission={hasPermission}
        onClick={() => setSetupVisibility(true)}
      >
        Add New Integration
      </RestrictedButton>
      <IntegrationConfigsTable
        integration={integration}
        integrationConfigs={integrationConfigs}
        hasPermission={hasPermission}
      />
      <IntegrationConfigSetup
        integration={integration}
        visible={setupVisiblity}
        onCancel={() => setSetupVisibility(false)}
      />
    </WorkspaceLayout>
  )
}

const withNotFound = withNotFoundHandler(({ workspace, integration }) => {
  return !workspace || !integration
})

export default compose(
  withGetWorkspaceBySlug,
  withGetIntegrationConfigs,
  withSuperUserAccess,
  withLargeLoader,
  withNotFound,
)(Integration)
