import React from "react"
import { Icon, Input } from "antd"
import { copyToClipboard } from "lib/utilities"

const CopyInput = ({ value, ...restProps }) => (
  <Input
    type="text"
    value={value}
    addonAfter={<Icon type="copy" onClick={() => copyToClipboard(value)} />}
    {...restProps}
  />
)

export default CopyInput
