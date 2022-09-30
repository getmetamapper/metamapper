import React, { Component } from "react"
import { Table } from "antd"
import Markdown from "react-markdown"
import BooleanIndicator from "app/Common/BooleanIndicator"

class CheckExecutionResults extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Description",
        dataIndex: "expectation",
        key: "expectation",
        render: expectation => <Markdown>{expectation.description}</Markdown>
      },
      {
        title: "Passed?",
        dataIndex: "passed",
        key: "passed",
        align: "center",
        render: passed => <BooleanIndicator value={passed} />
      },
    ]

    this.state = {
      dataSource: props.results
    }
  }

  renderExpandedRow = (record) => {
    const response = {
      'testCaseValue': record.expectedValue,
      'observedValue': record.observedValue,
    }
    return (
      <code style={{ whiteSpace: 'pre', fontWeight: 400 }}>
        {JSON.stringify(response, null, 2)}
      </code>
    )
  }

  render() {
    const { dataSource } = this.state
    return (
      <Table
        rowKey="id"
        dataSource={dataSource}
        pagination={false}
        columns={this.columns}
        expandedRowRender={this.renderExpandedRow}
        locale={{ emptyText: 'No expectations could be evaluated.' }}
      />
    )
  }
}

export default CheckExecutionResults
