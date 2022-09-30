import React, { Fragment } from "react"
import { Helmet } from "react-helmet"
import { compose } from "react-apollo"
import { Card, Col, Row, Tabs } from "antd"
import withGetWorkspaceUser from "graphql/withGetWorkspaceUser"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import { withLargeLoader } from "hoc/withLoader"
import Breadcrumbs from "app/Navigation/Breadcrumbs"
import UserProfileInner from "app/Users/UserProfileInner"
import GroupsTable from "app/WorkspaceSettings/Groups/GroupsTable"

const breadcrumbs = (workspaceSlug, user) => {
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
      label: "Users",
      to: `/${workspaceSlug}/settings/users`,
    },
    {
      label: user.name,
    },
  ]
}

const UserProfile = ({ currentWorkspace, workspaceUser, recentUserActivities }) => (
  <Fragment>
    <Helmet>
      <title>User - {workspaceUser.name} - Metamapper</title>
    </Helmet>
    <Row className="user-profile">
      <Col span={8} offset={8}>
        <div className="breadcrumbs-wrapper">
          <Breadcrumbs breadcrumbs={breadcrumbs(currentWorkspace.slug, workspaceUser)} />
        </div>
        <Card data-test="UserProfile">
          <div className="user-profile-header">
            <UserProfileInner user={workspaceUser} avatarSize={64} />
          </div>
          <Tabs defaultActiveKey="1" onChange={null}>
            <Tabs.TabPane tab="Groups" key="1">
              <GroupsTable groups={workspaceUser.workspaceGroups} showUsersCount={false} />
            </Tabs.TabPane>
          </Tabs>
        </Card>
      </Col>
    </Row>
  </Fragment>
)

const withNotFound = withNotFoundHandler(({ workspaceUser }) => {
  return !workspaceUser || !workspaceUser.hasOwnProperty("email")
})

export default compose(withGetWorkspaceUser, withLargeLoader, withNotFound)(UserProfile)
