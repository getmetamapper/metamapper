import React from "react"
import { Avatar, Tooltip } from "antd"

const SSOProviderIcon = ({ provider, label, protocol, ...restProps }) => (
  <span className="sso-provider-icon">
    <Tooltip title={label}>
      <Avatar
        shape="square"
        src={`/assets/static/img/sso/${protocol.toLowerCase()}/${provider.toLowerCase()}.png`}
        {...restProps}
      />
    </Tooltip>
  </span>
)

export default SSOProviderIcon
