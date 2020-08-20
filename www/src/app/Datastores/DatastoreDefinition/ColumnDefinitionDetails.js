import React from "react"
import { Drawer } from "antd"
import { compose } from "react-apollo"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import CreateComment from "app/Comments/CreateComment"
import CommentThread from "app/Comments/CommentThread"

const ColumnDefinitionDetails = ({
  column,
  hasPermission,
  loading,
  onClose,
  table,
  visible,
}) => (
  <Drawer
    title={
      <>
        <small>{table.schema.name}.</small>
        <small>{table.name}.</small>
        <span>{column.name}</span>
      </>
    }
    visible={visible}
    onClose={onClose}
    width={600}
    placement="right"
    className="column-comment-thread"
  >
    <CreateComment
      parentId={null}
      contentObject={column}
      loading={loading}
      hasPermission={hasPermission}
    />
    <CommentThread
      contentType="COLUMN"
      contentObject={column}
      loading={loading}
    />
  </Drawer>
)

export default compose(
  withWriteAccess,
  withLargeLoader
)(ColumnDefinitionDetails)
