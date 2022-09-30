import React from "react"
import { Divider } from "antd"
import { compose } from "react-apollo"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import UpdateWorkspace from "app/WorkspaceSettings/General/UpdateWorkspace"
import DeleteWorkspace from "app/WorkspaceSettings/General/DeleteWorkspace"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
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
      label: "General",
      to: `/${slug}/settings`,
    },
  ]
}

const General = ({ workspace, loading }) => (
  <WorkspaceLayout
    title={`General Settings - ${workspace.slug} - Metamapper`}
    breadcrumbs={breadcrumbs}
  >
    <h2>General Settings</h2>
    <Divider />
    <div className="update-workspace-metadata">
      <h3>Update workspace information</h3>
      <UpdateWorkspace workspace={workspace} loading={loading} />
    </div>
    <Divider />
    <div className="delete-workspace">
      <h3>Delete this workspace</h3>
      <p>
        Once you delete a workspace, there is no going back. Please be certain.
      </p>
      <DeleteWorkspace workspace={workspace} loading={loading} />
    </div>
  </WorkspaceLayout>
)

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace || !workspace.hasOwnProperty("id")
})

export default compose(
  withGetWorkspaceBySlug,
  withLargeLoader,
  withNotFound,
)(General)
