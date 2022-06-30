import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Table } from "antd"
import { ellipsis } from "lib/utilities"
import { withUserContext } from "context/UserContext"
import { withLargeLoader } from "hoc/withLoader"
import BooleanStatus from "app/Common/BooleanStatus"
import FromNow from "app/Common/FromNow"
import StatusBadge from "app/Common/StatusBadge"
import UserAvatar from "app/Common/UserAvatar"

class ChecksTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Name",
        dataIndex: "name",
        align: "left",
        render: name => <b title={name}>{ellipsis(name, 42)}</b>,
      },
      {
        title: "Created By",
        dataIndex: "creator",
        align: "center",
        render: (creator) => (
          <UserAvatar tooltip={creator.name} {...creator} />
        )
      },
      {
        title: "Status",
        dataIndex: "isEnabled",
        align: "left",
        render: isEnabled => <BooleanStatus isEnabled={isEnabled} />
      },
      {
        title: "Lastest Execution",
        align: "left",
        render: ({ lastExecution }) => lastExecution && <StatusBadge status={lastExecution.status} />
      },
      {
        title: "Last Executed",
        align: "left",
        render: ({ lastExecution }) => lastExecution && <FromNow time={lastExecution.finishedAt} />
      },
    ]
  }

  handleNavigate = (datastore, check) => {
    const {
      currentWorkspace: { slug },
      history,
    } = this.props

    history.push(`/${slug}/datastores/${datastore.slug}/checks/${check.pk}`)
  }

  render() {
    const { datastore, checks } = this.props
    return (
      <span className="checks-table" data-test="ChecksTable">
        <Table
          rowKey="pk"
          dataSource={checks}
          pagination={false}
          columns={this.columns}
          onRow={(check) => {
            return {
              onClick: (event) => this.handleNavigate(datastore, check),
            }
          }}
        />
      </span>
    )
  }
}

export default compose(withRouter, withUserContext, withLargeLoader)(ChecksTable)
