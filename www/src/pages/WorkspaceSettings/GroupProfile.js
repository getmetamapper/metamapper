import React from "react"
import { compose } from "react-apollo"
import { Card, Col, Row } from "antd"
import withGetWorkspaceGroup from "graphql/withGetWorkspaceGroup"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import { withLargeLoader } from "hoc/withLoader"
import ManageGroupUsersTable from "app/WorkspaceSettings/Groups/ManageGroupUsersTable"
import Breadcrumbs from "app/Navigation/Breadcrumbs"
import GroupProfileInner from "app/Groups/GroupProfileInner"

const breadcrumbs = (workspaceSlug, group) => {
  return [
    {
      label: "Home",
      to: `/${workspaceSlug}/datastores`,
    },
    {
      label: "Workspace Settings",
      to: `/${workspaceSlug}/settings`,
    },
    {
      label: "Groups",
      to: `/${workspaceSlug}/settings/groups`,
    },
    {
      label: group.name,
    },
  ]
}

const GroupProfile = ({ currentWorkspace, workspaceGroup }) => (
  <Row className="group-profile">
    <Col span={8} offset={8}>
      <div className="breadcrumbs-wrapper">
        <Breadcrumbs breadcrumbs={breadcrumbs(currentWorkspace.slug, workspaceGroup)} />
      </div>
      <Card data-test="GroupProfile">
        <div className="group-profile-header">
          <GroupProfileInner group={workspaceGroup} avatarSize={64} showDescription />
        </div>
        <ManageGroupUsersTable
          group={workspaceGroup}
          hasPermission={false}
          onRemove={null}
        />
      </Card>
    </Col>
  </Row>
)

const withNotFound = withNotFoundHandler(({ workspaceGroup }) => {
  return !workspaceGroup || !workspaceGroup.hasOwnProperty("id")
})

export default compose(
  withGetWorkspaceGroup,
  withLargeLoader,
  withNotFound,
)(GroupProfile)
