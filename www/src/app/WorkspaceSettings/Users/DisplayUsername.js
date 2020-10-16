import React from "react"
import UserAvatar from "app/Common/UserAvatar"
import { coalesce } from "lib/utilities"
import Link from "app/Navigation/Link"

const DisplayUsername = ({ id, userId, pk, name, email, avatarUrl }) => (
  <div className="user-display-name">
    <UserAvatar pk={pk} name={name} email={email} avatarUrl={avatarUrl} />
    <div className="metadata">
      <div className="name">
        <Link to={`/settings/users/${userId ? userId : id}`}>{coalesce(name, email)}</Link>
      </div>
      <div className="email">{email}</div>
    </div>
  </div>
)

export default DisplayUsername
