import React, { Component } from "react"
import { Table } from "antd"
import moment from "moment"
import prettyMs from "pretty-ms"
import StatusBadge from "app/Common/StatusBadge"

class RunHistoryTable extends Component {
  constructor(props) {
    super(props);

    this.columns = [
      {
        title: "Status",
        dataIndex: "status",
        render: (status, { error }) => <StatusBadge status={status} />
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
            {finishedAt && prettyMs(moment(finishedAt).diff(startedAt))}
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
