import React, { Component } from "react"
import { Table, Tag, Popover } from "antd"
import moment from "moment"
import prettyMs from "pretty-ms"

class RunHistoryTable extends Component {
  constructor(props) {
    super(props)

    this.statusColors = {
      SUCCESS: "green",
      PENDING: "orange",
      FAILURE: "red",
      PARTIAL: "volcano",
    }

    this.columns = [
      {
        title: "Status",
        dataIndex: "status",
        render: (status, { error }) => (
          <Tag color={this.statusColors[status]}>{status}</Tag>
        ),
      },
      {
        title: "Start Time",
        dataIndex: "startedAt",
        render: (startedAt) => <>{moment(startedAt).fromNow()}</>,
      },
      {
        title: "Duration",
        render: ({ startedAt, finishedAt }) => (
          <>
            {finishedAt && (
              <span>{prettyMs(moment(finishedAt).diff(startedAt))}</span>
            )}
          </>
        ),
      },
    ]
  }

  render() {
    const { runs } = this.props
    return (
      <span data-test="RunHistoryTable">
        <Table
          rowKey="id"
          className="datastore-run-history"
          dataSource={runs}
          columns={this.columns}
          pagination={false}
        />
      </span>
    )
  }
}

RunHistoryTable.defaultProps = {
  runs: [],
}

export default RunHistoryTable
