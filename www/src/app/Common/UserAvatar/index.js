import React from "react"
import { Avatar, Tooltip } from "antd"
import { coalesce } from "lib/utilities"

const avatarColors = [
  { color: "#f56a00", backgroundColor: "#fde3cf" }, // orange
  { color: "#00f56a", backgroundColor: "#cffde3" }, // green
  { color: "#008bf5", backgroundColor: "#cfe9fd" }, // blue
  { color: "#f5008b", backgroundColor: "#fdcfe9" }, // pink
  { color: "#f50010", backgroundColor: "#fdcfd2" }, // red
  { color: "#f5e500", backgroundColor: "#fdfacf" }, // yellow
  { color: "#6a00f5", backgroundColor: "#e3cffd" }, // purple
]

const UserAvatar = ({ pk, name, email, tooltip, avatarUrl, noColor, size }) => (
  <div className="avatar">
    <Tooltip title={tooltip} placement="right">
      <Avatar
        src={avatarUrl}
        style={noColor ? { backgroundColor: "#cccccc" } : avatarColors[pk % avatarColors.length]}
        size={size}
      >
        {coalesce(name, email)[0].toUpperCase()}
      </Avatar>
    </Tooltip>
  </div>
)

UserAvatar.defaultProps = {
  email: null,
  name: null,
  noColor: false,
  size: 32,
  tooltip: null,
}

export default UserAvatar
