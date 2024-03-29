import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Table } from "antd"
import { withUserContext } from "context/UserContext"
import { withLargeLoader } from "hoc/withLoader"
import moment from "moment"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"

class DatastoreList extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        width: 45,
        render: (text, row) => <DatastoreEngineIcon datastore={row} />,
      },
      {
        title: "Name",
        dataIndex: "name",
        key: "name",
        align: "left",
        render: (text) => <span className="datastore-name">{text}</span>,
      },
      {
        title: "Last Synced On",
        dataIndex: "latestRun",
        key: "latestRun",
        render: (latestRun) => (
          <>
            {latestRun && moment(latestRun.createdOn).format("MMMM Do, YYYY")}
          </>
        ),
      },
    ]
  }

  handleNavigate = (datastore) => {
    const {
      currentWorkspace: { slug },
      history,
    } = this.props

    history.push(`/${slug}/datastores/${datastore.slug}`)
  }

  render() {
    const { datastores } = this.props
    return (
      <span data-test="DatastoreList">
        <Table
          rowKey="id"
          dataSource={datastores}
          pagination={false}
          columns={this.columns}
          onRow={(datastore) => {
            return {
              onClick: () => this.handleNavigate(datastore)
            }
          }}
        />
      </span>
    )
  }
}

export default compose(
  withRouter,
  withUserContext,
  withLargeLoader
)(DatastoreList)
