import React from "react"
import { Icon, Tag, Tooltip } from "antd"

const TablePopularityBadge = ({
  popularityScore,
  totalQueries,
  totalUsers,
  windowInDays,
}) => (
  <Tooltip
    title={
      popularityScore
        ? `This table has been queried ${totalQueries} time(s) by ${totalUsers} user(s) over the past ${windowInDays} day(s).`
        : "Not enough data available for popularity score."
    }
  >
    <Tag>
      <Icon type="rocket" theme="twoTone" />
      <span className="popularity-score">{popularityScore || "--"}</span>
    </Tag>
  </Tooltip>
)

export default TablePopularityBadge
