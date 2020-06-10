import React from "react"
import { Icon } from "antd"

const BooleanIndicator = ({ value }) => (
  <>
    {value ? (
      <Icon type="check-circle" theme="twoTone" twoToneColor="#52c41a" />
    ) : (
      <Icon type="close-circle" theme="twoTone" twoToneColor="#f5222d" />
    )}
  </>
)

export default BooleanIndicator
