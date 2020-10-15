import React, { Component } from "react"
import { Tag } from "antd"
import { map } from "lodash"
import ExportableTable from "app/Common/ExportableTable"
import BooleanIndicator from "app/Common/BooleanIndicator"

class IndexDefinitionTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Index Name",
        dataIndex: "name",
        key: "name",
      },
      {
        title: "Primary",
        dataIndex: "isPrimary",
        key: "isPrimary",
        render: (isPrimary) => <BooleanIndicator value={isPrimary} />,
      },
      {
        title: "Unique",
        dataIndex: "isUnique",
        key: "isUnique",
        render: (isUnique) => <BooleanIndicator value={isUnique} />,
      },
      {
        title: "Column(s)",
        dataIndex: "columns",
        key: "columns",
        render: (columns) => (
          <>
            {map(columns, (column) => (
              <Tag>{column.name}</Tag>
            ))}
          </>
        ),
      },
    ]

    this.headers = [
      {
        label: "index",
        key: "name",
      },
      {
        label: "primary",
        key: "isPrimary",
      },
      {
        label: "unique",
        key: "isUnique",
      },
      {
        label: "columns",
        key: "columns",
        transformColumn: (value) => map(value, 'name').join(',')
      },
    ]
  }

  render() {
    const { dataSource } = this.props
    return (
      <span data-test="IndexDefinitionTable">
        <ExportableTable
          rowKey="id"
          className="datastore-indexes"
          dataSource={dataSource}
          columns={this.columns}
          headers={this.headers}
          pagination={false}
        />
      </span>
    )
  }
}

IndexDefinitionTable.defaultProps = {
  dataSource: [],
}

export default IndexDefinitionTable
