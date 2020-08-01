import React from "react"
import { compose } from "react-apollo"
import { withLargeLoader } from "hoc/withLoader"
import GroupsTable from "app/WorkspaceSettings/Groups/GroupsTable"
import withGetWorkspaceGroups from "graphql/withGetWorkspaceGroups"

const WorkspaceGroupsTable = ({ workspaceGroups, ...restProps }) => (
  <GroupsTable groups={workspaceGroups} {...restProps} />
)

export default compose(withGetWorkspaceGroups, withLargeLoader)(WorkspaceGroupsTable)
