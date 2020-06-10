import React from "react"
import UserAvatar from "app/Common/UserAvatar"
import { coalesce } from "lib/utilities"

const DisplayUsername = ({ pk, name, email }) => (
  <div className="user-display-name">
    <UserAvatar pk={pk} name={name} email={email} />
    <div className="metadata">
      <div className="name">{coalesce(name, email)}</div>
      <div className="email">{email}</div>
    </div>
  </div>
)

export default DisplayUsername
