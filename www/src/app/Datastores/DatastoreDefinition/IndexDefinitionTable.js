import React, { Component } from "react"
import { Table, Tag } from "antd"
import { map } from "lodash"
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
  }

  render() {
    const { dataSource } = this.props
    return (
      <span data-test="IndexDefinitionTable">
        <Table
          rowKey="id"
          className="datastore-indexes"
          dataSource={dataSource}
          columns={this.columns}
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
