import React, { Component } from "react"
import { Icon, Table, Tooltip } from "antd"
import moment from "moment"
import { renderRevisionText } from "./RevisionText"
import { renderRevisionIcon } from "./RevisionIcon"

class TableRevisionLog extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        dataIndex: "action",
        render: renderRevisionIcon,
      },
      {
        title: (currentPageData) => (
          <>
            <span className="mr-10">Change Detected At</span>
            <Tooltip title="When Metamapper discovered the change – not necessarily when it actually happened.">
              <Icon type="question-circle" theme="filled" />
            </Tooltip>
          </>
        ),
        dataIndex: "createdAt",
        key: "createdAt",
        render: (createdAt) => moment(createdAt).format(),
      },
      {
        title: "Activity",
        render: renderRevisionText,
      },
    ]
  }

  render() {
    const { revisions } = this.props
    return (
      <div className="table-revision-log" data-test="TableRevisionLog">
        <Table
          rowKey="id"
          dataSource={revisions}
          columns={this.columns}
          pagination={false}
        />
      </div>
    )
  }
}

TableRevisionLog.defaultProps = {
  revisions: [],
}

export default TableRevisionLog
