import React, { Fragment } from "react"
import moment from "moment"
import { Icon, Tooltip } from "antd"
import GroupAvatar from "app/Common/GroupAvatar"
import Link from "app/Navigation/Link"

const GroupProfileInner = ({
  avatarSize,
  group,
  showDescription,
  showLink,
}) => (
   <Fragment>
      <div className="profile-avatar">
        <GroupAvatar size={avatarSize} {...group} />
      </div>
      <div className="profile-metadata">
        <span className="profile-name">
          {showLink ? <Link to={`/settings/groups/${group.id}`}>{group.name}</Link> : group.name}
        </span>
        <ul>
          <li>
            <Tooltip title="Created On" placement="bottom">
              <Icon type="clock-circle" /> {moment(group.createdAt).format('MMM DD, YYYY')}
            </Tooltip>
          </li>
        </ul>
        {showDescription && (
          <div className="group-profile-description">{group.description}</div>
        )}
      </div>
   </Fragment>
)

GroupProfileInner.defaultProps = {
    avatarSize: 32,
    showDescription: false,
    showLink: false,
}

export default GroupProfileInner
