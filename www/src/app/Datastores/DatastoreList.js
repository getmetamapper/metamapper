import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Table, Tag } from "antd"
import { withUserContext } from "context/UserContext"
import moment from "moment"
import withLoader from "hoc/withLoader"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"

class DatastoreList extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        width: 45,
        render: (text, row, index) => <DatastoreEngineIcon datastore={row} />,
      },
      {
        title: "Name",
        dataIndex: "name",
        key: "name",
        align: "left",
        render: (text, row, index) => (
          <span className="datastore-name">{text}</span>
        ),
      },
      {
        title: "Status",
        dataIndex: "isEnabled",
        key: "isEnabled",
        render: (isEnabled) => (
          <Tag color={isEnabled ? "blue" : "volcano"}>
            {isEnabled ? "Enabled" : "Disabled"}
          </Tag>
        ),
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
              onClick: (event) => this.handleNavigate(datastore), // click row
            }
          }}
        />
      </span>
    )
  }
}

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

const enhance = compose(withRouter, withUserContext, withLargeLoader)

export default enhance(DatastoreList)
