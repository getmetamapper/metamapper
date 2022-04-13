import React from "react"
import { Tag } from "antd"

const colorMap = {
  SUCCESS: "green",
  PENDING: "orange",
  FAILURE: "red",
  PARTIAL: "volcano",
}

const StatusBadge = ({ status, ...restProps }) => (
  <Tag color={colorMap[status]} {...restProps}>
    {status}
  </Tag>
)

export default StatusBadge
