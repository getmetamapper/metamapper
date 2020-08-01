import React, { Component, Fragment } from "react"
import { Table } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import AvatarStacked from "app/Common/AvatarStacked"
import Link from "app/Navigation/Link"
import withGetWorkspaceGroups from "graphql/withGetWorkspaceGroups"

class GroupsTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Name",
        render: ({ id, name }) => <Link to={`/settings/groups/${id}`}>{name}</Link>
      },
      {
        title: "Users",
        render: (record) => (
          <span onClick={() => props.onManage(record)}>
            <AvatarStacked
              users={[]}
              count={record.usersCount}
              title={null}
            />
          </span>
        )
      },
      {
        title: "Description",
        dataIndex: "description",
        key: "description",
      },
    ]

    if (props.hasPermission) {
      this.columns.push({
        align: "right",
        render: (record) => (
          <Fragment>
            {/* eslint-disable-next-line*/}
            <a
              role="button"
              onClick={() => props.onUpdate(record)}
              className="mr-10"
            >
              Edit
            </a>
            {/* eslint-disable-next-line*/}
            <a role="button" onClick={() => props.onDelete(record)}>
              Delete
            </a>
          </Fragment>
        ),
      })
    }
  }

  render() {
    const { workspaceGroups } = this.props
    return (
      <span className="groups-table" data-test="GroupsTable">
        <Table
          rowKey="id"
          dataSource={workspaceGroups}
          columns={this.columns}
          pagination={false}
        />
      </span>
    )
  }
}

export default withGetWorkspaceGroups(withLargeLoader(GroupsTable))
