import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Icon, Table, Tooltip, Tag } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { components } from "app/Common/EditableCell"
import BooleanIndicator from "app/Common/BooleanIndicator"
import UpdateColumnMetadata from "graphql/mutations/UpdateColumnMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class ColumnDefinitionTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        align: "center",
        render: (row) => (
          <div className={row.commentsCount > 0 ? "has-comments" : ""}>
            <Tooltip title={`${row.commentsCount} comment(s)`}>
              <Icon
                type="message"
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
        render: (name) => <span className="column-name">{name}</span>,
      },
      {
        title: "Data Type",
        dataIndex: "fullDataType",
        key: "fullDataType",
        render: (fullDataType) => <Tag>{fullDataType}</Tag>,
      },
      {
        title: "Nullable",
        dataIndex: "isNullable",
        align: "center",
        render: (isNullable) => <BooleanIndicator value={isNullable} />,
      },
      {
        title: "Default Value",
        dataIndex: "defaultValue",
        key: "defaultValue",
      },
      {
        title: "Description",
        dataIndex: "shortDesc",
        key: "shortDesc",
        editable: true,
      },
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

    this.props.handleMutation(payload, ({ data }) => {
      const { column } = data.updateColumnMetadata

      row.shortDesc = column.shortDesc

      this.updateRow(row)
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
        <Table
          rowKey="id"
          rowClassName={() => "editable-row"}
          className="datastore-columns"
          components={components}
          dataSource={dataSource}
          columns={columns}
          pagination={false}
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
