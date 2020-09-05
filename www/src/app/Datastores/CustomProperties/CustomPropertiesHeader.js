import React from "react"
import { Button, Tooltip } from "antd"
import Link from "app/Navigation/Link"

const CustomPropertiesHeader = ({ isEditable, onToggleEdit }) => (
  <div className="custom-fields-toolbar">
    {isEditable && (
      <Tooltip title="Edit custom properties">
        <span className="custom-fields-toolbar-item" data-test="CustomProperties.Edit">
          <Button size="small" icon="edit" onClick={onToggleEdit} />
        </span>
      </Tooltip>
    )}
    <Tooltip title="Manage custom properties">
      <span className="custom-fields-toolbar-item" data-test="CustomProperties.Manage">
        <Link to="/settings/customproperties" target="_blank">
          <Button size="small" icon="tool" />
        </Link>
      </span>
    </Tooltip>
  </div>
)

export default CustomPropertiesHeader
