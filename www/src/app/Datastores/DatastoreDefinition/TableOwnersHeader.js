import React, { useState, Fragment } from "react"
import { Button, Popover, Tooltip } from "antd"
import CreateTableOwner from "app/Datastores/DatastoreDefinition/CreateTableOwner"

const TableOwnersHeader = ({ isEditing, isEditable, isEmpty, onToggleEdit, objectId, ownerIds }) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="table-owners-toolbar">
      {isEditable && (
        <Fragment>
          {!isEmpty && (
            <Tooltip title="Edit data owners">
              <span className="table-owners-toolbar-item" data-test="TableOwnersHeader.Edit">
                <Button size="small" icon={isEditing ? 'check' : 'edit'} onClick={onToggleEdit} />
              </span>
            </Tooltip>
          )}
          <Popover placement="right" visible={open} content={
            <CreateTableOwner
              objectId={objectId}
              ownerIds={ownerIds}
              open={open}
              onClose={() => setOpen(false)}
            />
          }>
            <span className="table-owners-toolbar-item" data-test="TableOwnersHeader.Add" onClick={() => setOpen(!open)}>
              <Button size="small" icon={open ? 'close' : 'plus'} />
            </span>
          </Popover>
        </Fragment>
      )}
    </div>
  )
}

export default TableOwnersHeader
