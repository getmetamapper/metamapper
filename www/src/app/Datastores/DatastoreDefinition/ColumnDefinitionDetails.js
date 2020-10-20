import React, { Component } from "react"
import { Alert, Drawer, Menu } from "antd"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import CreateComment from "app/Comments/CreateComment"
import CommentThread from "app/Comments/CommentThread"
import Readme from "app/Datastores/Readme/Readme"
import Link from "app/Navigation/Link"

class ColumnDefinitionDetails extends Component {
  state = { current: "readme" }

  handleClick = ({ key }) => {
    this.setState({ current: key })
  }

  getBaseUrl = () => {
    const {
      match: {
        params: {
          datastoreSlug,
          schemaName,
          tableName,
        },
      }
    } = this.props
    return (
      `/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}/columns`
    )
  }

  getReadmeUrl = (column) => {
    return `${this.getBaseUrl()}/${column.name}/readme/edit`
  }

  render() {
    const { current } = this.state
    const {
      column,
      table,
      onClose,
      visible,
      hasPermission,
      loading,
    } = this.props
    return (
      <Drawer
        title={
          <>
            <small>{table.schema.name}.</small>
            <small>{table.name}.</small>
            <span>{column.name}</span>
          </>
        }
        visible={visible}
        width={800}
        placement="right"
        onClose={onClose}
        className="column-definition-details"
      >
        <Menu
          onClick={this.handleClick}
          selectedKeys={[current]}
          mode="horizontal"
        >
          <Menu.Item key="readme">README</Menu.Item>
          <Menu.Item key="discussion">Discussion</Menu.Item>
        </Menu>
        {visible && current === "readme" && (
          <div className="column-definition-readme" data-test="ColumnReadme">
            {hasPermission  && (
              <Alert message={
                <span>
                  You can <Link to={this.getReadmeUrl(column)} data-test="ColumnReadme.Edit">click here</Link> to edit this README.
                </span>
              }/>
            )}
            <Readme markdown={column.readme} />
          </div>
        )}
        {visible && current === "discussion" && (
          <div className="column-definition-comments">
            <CreateComment
              parentId={null}
              contentObject={column}
              loading={loading}
              hasPermission={hasPermission}
              onSubmit={() => column.commentsCount += 1}
            />
            <CommentThread
              contentType="COLUMN"
              contentObject={column}
              loading={loading}
              onCreate={() => column.commentsCount += 1}
              onDelete={() => column.commentsCount -= 1}
            />
          </div>
        )}
      </Drawer>
    )
  }
}

export default compose(
  withRouter,
  withWriteAccess,
  withLargeLoader,
)(ColumnDefinitionDetails)
