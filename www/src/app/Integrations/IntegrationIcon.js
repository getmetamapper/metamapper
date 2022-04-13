import React from "react"
import { Avatar, Tooltip } from "antd"

const IntegrationIcon = ({
  integration,
  customStyles,
  tooltip,
  noTooltip,
}) => (
  <span className="integration-icon">
    <Tooltip title={noTooltip ? null : (tooltip || integration)}>
      <Avatar
        shape="square"
        src={`/assets/static/img/integrations/${integration.toLowerCase()}.png`}
        style={customStyles}
      />
    </Tooltip>
  </span>
)

IntegrationIcon.defaultProps = {
  customStyles: {},
  tooltip: null,
  noTooltip: false
}

export default IntegrationIcon
