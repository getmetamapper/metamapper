import React, { Component } from "react"
import { compose } from "react-apollo"
import { Tooltip, Tag, Table } from "antd"
import { find } from "lodash"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import { PERMISSION_CHOICES } from "lib/constants"
import Link from "app/Navigation/Link"
import DeleteSSOConnection from "./DeleteSSOConnection"
import EnableSSOConnection from "./EnableSSOConnection"
import SSOProviderIcon from "./SSOProviderIcon"

class SSOConnectionsTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Name",
        render: ({ pk, name, protocol }) => (
          <span data-test="SSOConnectionsTable.Name">
            {protocol.toUpperCase() === "SAML2" ? (
              <Link to={`/settings/authentication/${pk}/edit`}>{name}</Link>
            ) : (
              <Tooltip title="You cannot edit OAuth2 connections">
                {name}
              </Tooltip>
            )}
          </span>
        ),
      },
      {
        title: "Provider",
        dataIndex: "provider",
        key: "provider",
        align: "center",
        render: (provider) => (
          <SSOProviderIcon {...find(props.ssoProviders, { provider })} />
        ),
      },
      {
        title: "Default Role",
        dataIndex: "defaultPermissions",
        key: "defaultPermissions",
        render: (defaultPermissions) => (
          <Tag>{PERMISSION_CHOICES[defaultPermissions]}</Tag>
        ),
      },
      {
        title: "Audience",
        dataIndex: "audience",
        key: "audience",
      },
      {
        align: "right",
        render: ({ id, isEnabled }) => (
          <>
            <EnableSSOConnection connectionId={id} isEnabled={isEnabled} />
            <DeleteSSOConnection connectionId={id} />
          </>
        ),
      },
    ]
  }

  render() {
    const { ssoConnections } = this.props
    return (
      <span className="sso-connections-table" data-test="SSOConnectionsTable">
        <Table
          rowKey="pk"
          dataSource={ssoConnections}
          columns={this.columns}
          pagination={false}
        />
      </span>
    )
  }
}

export default compose(withSuperUserAccess, withLargeLoader)(SSOConnectionsTable)
