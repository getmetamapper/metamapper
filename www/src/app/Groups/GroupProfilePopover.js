import React from "react"
import { compose } from "react-apollo"
import { Popover } from "antd"
import withGetWorkspaceGroupById from "graphql/withGetWorkspaceGroupById"
import { withPopoverLoader } from "hoc/withLoader"
import GroupProfileInner from "app/Groups/GroupProfileInner"

const GroupProfilePopoverContent = ({ workspaceGroup }) => (
  <div className="group-profile-popover">
    <GroupProfileInner group={workspaceGroup} showLink />
  </div>
)

const WrappedGroupProfilePopoverContent = compose(
    withGetWorkspaceGroupById,
    withPopoverLoader,
)(GroupProfilePopoverContent)

const GroupProfilePopover = ({ children, groupId }) => (
  <Popover content={<WrappedGroupProfilePopoverContent groupId={groupId} />} placement="right">
    {children}
  </Popover>
)

export default GroupProfilePopover
