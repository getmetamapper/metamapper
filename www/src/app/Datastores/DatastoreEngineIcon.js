import React from "react"
import { Avatar, Tooltip } from "antd"

const DatastoreEngineIcon = ({
  datastore: {
    jdbcConnection: { engine },
  },
  customStyles,
  tooltip,
  noTooltip,
}) => (
  <span className="datastore-engine-icon">
    <Tooltip title={noTooltip ? null : (tooltip || engine)}>
      <Avatar
        shape="square"
        src={`/assets/static/img/datastores/dialects/${engine.toLowerCase()}.png`}
        style={customStyles}
      />
    </Tooltip>
  </span>
)

DatastoreEngineIcon.defaultProps = {
  customStyles: {},
  tooltip: null,
  noTooltip: false
}

export default DatastoreEngineIcon
