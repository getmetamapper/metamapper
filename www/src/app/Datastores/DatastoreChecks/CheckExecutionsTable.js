import React, { Component } from "react"
import { Table } from "antd"
import FromNow from "app/Common/FromNow"
import StatusBadge from "app/Common/StatusBadge"
import moment from "moment"
import prettyMs from "pretty-ms"

class CheckExecutionsTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Status",
        dataIndex: "status",
        render: status => <StatusBadge status={status} />
      },
      {
        title: "Started",
        dataIndex: "startedAt",
        key: "startedAt",
        render: startedAt => startedAt && <FromNow time={startedAt} />
      },
      {
        title: "Duration",
        render: ({ startedAt, finishedAt }) => (
          <>
            {finishedAt && prettyMs(moment(finishedAt).diff(startedAt))}
          </>
        ),
      },
      {
        title: "Tests Passed",
        render: ({ failsCount, tasksCount }) => (
          <span className={failsCount > 0 && "failed-check"}>
            {tasksCount - failsCount} / {tasksCount}
          </span>
        ),
      },
    ]
  }

  render() {
    const { checkExecutions } = this.props
    return (
      <span className="check-executions-table" data-test="CheckExecutionsTable">
        <Table
          rowKey="pk"
          dataSource={checkExecutions}
          pagination={{ simple: true, pageSize: 15 }}
          columns={this.columns}
          onRow={(checkExecution) => {
            return {
              onClick: (event) => this.props.onOpenDetails(checkExecution),
            }
          }}
        />
      </span>
    )
  }
}

export default CheckExecutionsTable
