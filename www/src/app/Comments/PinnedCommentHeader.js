import React from "react"
import { Icon } from "antd"

const PinnedCommentHeader = ({ pinnedAt, pinnedBy }) => (
  <div className="pinned-comment-header">
    <Icon type="pushpin" /> <span>Pinned by {pinnedBy.name}</span>
  </div>
)

export default PinnedCommentHeader
