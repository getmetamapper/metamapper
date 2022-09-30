import React from "react"
import { Tooltip } from "antd"
import moment from "moment"
import { TIMESTAMP_FORMAT } from "lib/constants"

const FromNow = ({ time, format }) => (
  <Tooltip title={moment(time).format(format)}>
    {moment(time).fromNow()}
  </Tooltip>
)

FromNow.defaultProps = {
  format: TIMESTAMP_FORMAT,
}

export default FromNow
