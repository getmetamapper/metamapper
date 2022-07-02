import React from "react"
import { compose } from "react-apollo"
import { Divider } from "antd"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import WorkspaceUsersTable from "app/WorkspaceSettings/Users/WorkspaceUsersTable"
import InviteUserToWorkspace from "app/WorkspaceSettings/Users/InviteUserToWorkspace"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"
import withGetWorkspaceUsers from "graphql/withGetWorkspaceUsers"

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
      label: "Users",
      to: `/${slug}/settings/users`,
    },
  ]
}

const Users = ({ workspace, workspaceUsers, loading }) => (
  <WorkspaceLayout
    title={`Users - ${workspace.slug} - Metamapper`}
    breadcrumbs={breadcrumbs}
  >
    <h2>Users</h2>
    <Divider />
    <div className="workspace-users">
      <InviteUserToWorkspace loading={loading} workspace={workspace} />
      <div className="team-member-list">
        <WorkspaceUsersTable
          loading={loading}
          workspace={workspace}
          workspaceUsers={workspaceUsers}
        />
      </div>
    </div>
  </WorkspaceLayout>
)

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace || !workspace.hasOwnProperty("id")
})

export default compose(
  withGetWorkspaceBySlug,
  withGetWorkspaceUsers,
  withLargeLoader,
  withNotFound,
)(Users)
