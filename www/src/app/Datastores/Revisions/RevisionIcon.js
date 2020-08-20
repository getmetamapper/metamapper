import React from "react"
import { Icon, Tooltip } from "antd"

const CreatedRevision = (props) => (
  <Tooltip title="Created">
    <Icon type="file-add" theme="twoTone" twoToneColor="#52c41a" />
  </Tooltip>
)

const ModifiedRevision = (props) => (
  <Tooltip title="Modified">
    <Icon type="diff" theme="twoTone" twoToneColor="#faad14" />
  </Tooltip>
)

const DroppedRevision = (props) => (
  <Tooltip title="Dropped">
    <Icon type="file-excel" theme="twoTone" twoToneColor="#f5222d" />
  </Tooltip>
)

export const renderRevisionIcon = (action) => {
  if (!action) return null

  const switchBoard = {
    "A_1": CreatedRevision,
    "A_2": ModifiedRevision,
    "A_3": DroppedRevision,
  }

  const Component = switchBoard[action]

  return <Component action={action} />
}
