import React, { Component } from "react"
import { Alert, Icon, Table } from "antd"
import { first, keys, isEqual } from "lodash"
import withLoader from "hoc/withLoader"

const defaultColumns = [
  {
    title: '',
  },
]

class CheckSqlPreviewResults extends Component {
  shouldComponentUpdate({ queryResults, sqlException }) {
    return !isEqual(queryResults, this.props.queryResults) || !isEqual(sqlException, this.props.sqlException)
  }

  getColumns() {
    let columns = keys(first(this.props.queryResults)).map(key => ({
      dataIndex: key,
      key,
      title: key,
      width: 250,
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
          scroll={{ x: 'max-content', y: 300 }}
          locale={{ emptyText: this.emptyText() }}
        />
      </div>
    )
  }
}

export default withLoader({
  indicator: <Icon type="loading" style={{ fontSize: 24 }} spin />,
  wrapperstyles: {
    textAlign: "center",
    paddingTop: "40px",
    paddingBottom: "40px",
    borderTop: "1px solid #e8e8e8",
    borderLeft: "1px solid #e8e8e8",
  },
})(CheckSqlPreviewResults)
