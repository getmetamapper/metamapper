import React from "react"
import { compose } from "react-apollo"
import { Popover } from "antd"
import withGetWorkspaceUserById from "graphql/withGetWorkspaceUserById"
import { withPopoverLoader } from "hoc/withLoader"
import UserProfileInner from "app/Users/UserProfileInner"

const UserPopoverContent = ({ workspaceUser }) => (
  <div className="user-profile-popover">
    <UserProfileInner user={workspaceUser} showLink />
  </div>
)

const WrappedUserPopoverContent = compose(
    withGetWorkspaceUserById,
    withPopoverLoader,
)(UserPopoverContent)

const UserProfilePopover = ({ children, userId }) => (
  <Popover content={<WrappedUserPopoverContent userId={userId} />} placement="right">
    {children}
  </Popover>
)

export default UserProfilePopover
