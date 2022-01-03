import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Card, Icon, Tooltip, Tag } from "antd"
import { isEmpty, pick, map, some, find } from "lodash"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { components } from "app/Common/EditableCell"
import FormLabel from "app/Common/FormLabel"
import ExportableTable from "app/Common/ExportableTable"
import BooleanIndicator from "app/Common/BooleanIndicator"
import UpdateColumnMetadata from "graphql/mutations/UpdateColumnMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class ColumnDefinitionTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        align: "center",
        width: 40,
        render: (row) => (
          <div className={row.commentsCount > 0 || (row.readme && row.readme.length > 0) ? "has-comments" : ""}>
            <Tooltip title="View column details">
              <Icon
                type="eye"
                className="column-comments-icon"
                onClick={() => props.onOpenDetails(row)}
              />
            </Tooltip>
          </div>
        ),
      },
      {
        key: "isPrimary",
        dataIndex: "isPrimary",
        align: "center",
        width: 40,
        render: (isPrimary) => (
          <>
            {isPrimary && (
              <Tooltip title="Primary Key">
                <Icon type="key" style={{ color: "#f3a50a" }} />
              </Tooltip>
            )}
          </>
        ),
      },
      {
        title: "Column",
        dataIndex: "name",
        key: "name",
        sorter: (a, b) => a.name.charCodeAt(0) - b.name.charCodeAt(0),
        render: (name) => <span className="column-name">{name}</span>,
      },
      {
        title: "Data Type",
        dataIndex: "fullDataType",
        key: "fullDataType",
        sorter: (a, b) => a.fullDataType.charCodeAt(0) - b.fullDataType.charCodeAt(0),
        render: (fullDataType) => <Tag>{fullDataType}</Tag>,
      },
      {
        title: "Description",
        dataIndex: "shortDesc",
        key: "shortDesc",
        editable: true,
        sorter: (a, b) => {
          if (!a.shortDesc) {
            return -1;
          }
          return a.shortDesc.charCodeAt(0) - b.shortDesc.charCodeAt(0)
        }
      },
    ]

    this.headers = [
      { label: "column", key: "name" },
      { label: "primary", key: "isPrimary" },
      { label: "nullable", key: "isNullable" },
      { label: "data_type", key: "fullDataType" },
      { label: "description", key: "shortDesc" },
      { label: "comment", key: "dbComment" },
      { label: "default_value", key: "defaultValue" },
    ]

    this.expandedColumns = [
      {
        title: "Comment",
        key: "dbComment",
        helpText: "This is the comment set within the database system.",
      },
      {
        title: "Default Value",
        key: "defaultValue",
        helpText: "This will be the value of the column if none is provided."
      }
    ]

    this.state = {
      dataSource: props.dataSource,
    }
  }

  handleSave = (row) => {
    const payload = {
      variables: {
        id: row.id,
        shortDesc: row.shortDesc,
      },
      successMessage: "Description was saved.",
    }

    const oldRow = find(this.props.dataSource, { id: row.id })

    if (row.shortDesc === oldRow.shortDesc) {
      return;
    }

    this.props.handleMutation(payload, ({ data }) => {
      const { column, errors } = data.updateColumnMetadata

      if (!errors) {
        row.shortDesc = column.shortDesc
        this.updateRow(row)
      }
    })
  }

  updateRow = (row) => {
    const newData = [...this.state.dataSource]
    const index = newData.findIndex((item) => row.id === item.id)
    const item = newData[index]
    newData.splice(index, 1, {
      ...item,
      ...row,
    })
    this.setState({ dataSource: newData })
  }

  shouldExpand = (record) => {
    return some(pick(record, map(this.expandedColumns, 'key')), (i) => !isEmpty(i))
  }

  renderExpandedRow = (record) => {
    return (
      <Card className="datastore-columns-expansion">
        {map(this.expandedColumns, ({ title, key, helpText }) => {
          if (isEmpty(record[key])) return null;
          return (
            <div className="datastore-columns-expansion-item">
              <FormLabel label={title} helpText={helpText} />
              <span>{record[key]}</span>
            </div>
          )
        })}
      </Card>
    )
  }

  render() {
    const { hasPermission } = this.props
    const { dataSource } = this.state
    const columns = this.columns.map((col) => {
      if (!hasPermission || !col.editable) {
        return col
      }
      return {
        ...col,
        onCell: (record) => ({
          record,
          editable: col.editable,
          dataIndex: col.dataIndex,
          title: col.title,
          handleSave: this.handleSave,
        }),
      }
    })

    return (
      <span data-test="ColumnDefinitionTable">
        <ExportableTable
          rowKey="id"
          className="datastore-columns"
          components={components}
          dataSource={dataSource}
          columns={columns}
          headers={this.headers}
          pagination={false}
          expandedRowRender={this.renderExpandedRow}
          rowClassName={record => (this.shouldExpand(record) ? "editable-row" : "editable-row not-expandable")}
          scroll={{ x: (window.innerWidth / 2) }}
        />
      </span>
    )
  }
}

ColumnDefinitionTable.defaultProps = {
  dataSource: [],
}

const enhance = compose(
  withWriteAccess,
  graphql(UpdateColumnMetadata),
  withGraphQLMutation
)

export default enhance(ColumnDefinitionTable)
