import React from "react"
import { Avatar, Tooltip } from "antd"

const DatastoreEngineIcon = ({
  datastore: {
    jdbcConnection: { engine },
  },
  customStyles,
  tooltip,
}) => (
  <span className="datastore-engine-icon">
    <Tooltip title={tooltip || engine}>
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
}

export default DatastoreEngineIcon
