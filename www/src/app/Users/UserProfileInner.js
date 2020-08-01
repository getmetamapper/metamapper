import React, { Fragment } from "react"
import moment from "moment"
import { Icon, Tooltip } from "antd"
import UserAvatar from "app/Common/UserAvatar"
import Link from "app/Navigation/Link"

const UserProfileInner = ({
  avatarSize,
  user,
  showDescription,
  showLink,
}) => (
   <Fragment>
      <div className="profile-avatar">
        <UserAvatar size={avatarSize} {...user} />
      </div>
      <div className="profile-metadata">
        <span className="profile-name">
          {showLink ? <Link to={`/settings/users/${user.id}`}>{user.name}</Link> : user.name}
        </span>
        <ul>
          <li>
            <Tooltip title="Email" placement="bottom">
              <Icon type="mail" /> <a href={`mailto:${user.email}`}>{user.email}</a>
            </Tooltip>
          </li>
          <li>
            <Tooltip title="Joined On" placement="bottom">
              <Icon type="clock-circle" /> {moment(user.createdAt).format('MMM DD, YYYY')}
            </Tooltip>
          </li>
        </ul>
      </div>
   </Fragment>
)

UserProfileInner.defaultProps = {
    avatarSize: 32,
    showDescription: false,
    showLink: false,
}

export default UserProfileInner
