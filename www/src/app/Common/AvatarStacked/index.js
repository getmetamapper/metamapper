import React from "react"
import { Avatar, Tooltip } from "antd"
import { map } from "lodash"

const AvatarStacked = ({ users, title, count }) => (
  <div className="ant-stacked-avatars">
    {map(users, ({ avatar }, idx) => (
      <Avatar src={avatar} icon="user" key={idx} />
    ))}
    <Tooltip title={title}>
      <Avatar className="ant-stacked-avatar">
        {count}
      </Avatar>
    </Tooltip>
  </div>
)

export default AvatarStacked
