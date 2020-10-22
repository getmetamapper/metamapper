import React from "react"
import { Tooltip } from "antd"
import moment from "moment"
import KeyValuePill from "app/Common/KeyValuePill"

const TableLastCommitTimestamp = ({ timestamp, loading }) => {
  if (loading || !timestamp) {
    return null
  }
  return (
    <Tooltip title={moment.utc(timestamp).fromNow()}>
      <div>
        <KeyValuePill
          keyname="Last Updated"
          value={moment(timestamp).format('YYYY-MM-DD HH:mm:ss [UTC]')}
        />
      </div>
    </Tooltip>
  )
}
export default TableLastCommitTimestamp
