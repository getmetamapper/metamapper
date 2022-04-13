import React, { Component } from "react"
import { Alert, Table } from "antd"
import { first, keys, isEqual } from "lodash"

const defaultColumns = [
  {
    title: ''
  }
];

class CheckSqlPreviewResults extends Component {
  shouldComponentUpdate({ queryResults, sqlException }) {
    return !isEqual(queryResults, this.props.queryResults) || !isEqual(sqlException, this.props.sqlException)
  }

  getColumns() {
    let columns = keys(first(this.props.queryResults)).map(key => ({
      title: key,
      key: key,
      dataIndex: key,
    }))

    if (columns.length === 0) {
      columns = defaultColumns
    }

    return columns
  }

  emptyText() {
    return this.props.queryResults === null
      ? 'The results of your query will appear here.'
      : 'No results.'
  }

  render() {
    const { queryResults, sqlException } = this.props
    return (
      <div className="check-sql-editor-preview-results">
        {sqlException && (
          <Alert
            showIcon
            message={<code>{sqlException}</code>}
            type="error"
          />
        )}
        <Table
          columns={this.getColumns()}
          dataSource={queryResults}
          pagination={false}
          scroll={{ x: 1500, y: 300 }}
          locale={{ emptyText: this.emptyText() }}
        />
      </div>
    )
  }
}

export default CheckSqlPreviewResults
