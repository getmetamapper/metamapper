import React, { Component } from "react"
import { compose } from "react-apollo"
import { Table } from "antd"
import moment from "moment"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import EnableApiToken from "app/WorkspaceSettings/Api/EnableApiToken"
import DeleteApiToken from "app/WorkspaceSettings/Api/DeleteApiToken"

class ApiTokensTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Name",
        dataIndex: "name",
        key: "name",
      },
      {
        title: "Enabled",
        align: "center",
        render: ({ id, isEnabled }) => (
          <EnableApiToken tokenId={id} isEnabled={isEnabled} />
        ),
      },
      {
        title: "Created",
        dataIndex: "createdAt",
        key: "createdAt",
        render: (createdAt) => moment(createdAt).format("MMMM Do, YYYY")
      },
      {
        align: "right",
        render: ({ id }) => (
          <>
            <DeleteApiToken tokenId={id} />
          </>
        ),
      },
    ]
  }

  render() {
    const { apiTokens } = this.props
    return (
      <span className="api-tokens-table" data-test="ApiTokensTable">
        <Table
          rowKey="pk"
          dataSource={apiTokens}
          columns={this.columns}
          pagination={false}
        />
      </span>
    )
  }
}

export default compose(withSuperUserAccess, withLargeLoader)(ApiTokensTable)
