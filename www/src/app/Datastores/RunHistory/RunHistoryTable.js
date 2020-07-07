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
    }

    this.columns = [
      {
        title: "Status",
        render: ({ status, error }) => (
          <>
            {status === "FAILURE" ? (
              <Popover content={<code>{error.excMessage}</code>} title="The following error was encountered:">
                <Tag color={this.statusColors[status]}>{status}</Tag>
              </Popover>
            ) : (
              <Tag color={this.statusColors[status]}>{status}</Tag>
            )}
          </>
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
      {
        title: "Changes Recorded",
        render: (record) => (
          <>
            {record.finishedAt && record.status !== "FAILURE" && (
              // eslint-disable-next-line
              <a role="button" onClick={() => this.props.onSelect(record)}>
                {record.revisionCount > 0 ? record.revisionCount : "no"}{" "}
                change(s) detected
              </a>
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
