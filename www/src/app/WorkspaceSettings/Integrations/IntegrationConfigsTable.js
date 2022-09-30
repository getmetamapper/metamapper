import React, { Component, Fragment } from "react"
import { Table, Tooltip } from "antd"
import moment from "moment"
import UpdateIntegrationConfig from "app/WorkspaceSettings/Integrations/UpdateIntegrationConfig"
import DeleteIntegrationConfig from "app/WorkspaceSettings/Integrations/DeleteIntegrationConfig"
import UserAvatar from "app/Common/UserAvatar"

class IntegrationConfigsTable extends Component {
  constructor(props) {
    super(props);

    this.columns = [
      {
        title: props.integration.details.find(v => v.isDisplay).label,
        dataIndex: "displayable",
        render: (displayable) => <b>{displayable}</b>
      },
      {
        title: "Created By",
        dataIndex: "createdBy",
        align: "center",
        render: (createdBy) => (
          <UserAvatar tooltip={createdBy.name} {...createdBy} />
        )
      },
      {
        title: "Created On",
        dataIndex: "createdAt",
        render: (createdAt) => <span>{moment(createdAt).format('MMMM Do, YYYY')}</span>
      },
      {
        align: "right",
        render: (record) => (
          <Fragment>
            <Tooltip title="Configure">
              <UpdateIntegrationConfig
                integration={props.integration}
                integrationConfig={record}
                hasPermission={props.hasPermission}
              />
            </Tooltip>
            <Tooltip title="Uninstall">
              <DeleteIntegrationConfig
                integration={props.integration}
                integrationConfig={record}
                hasPermission={props.hasPermission}
             />
            </Tooltip>
          </Fragment>
        ),
      }
    ];
  }

  render() {
    const { integrationConfigs } = this.props
    return (
      <div className="integration-configs-table" data-test="IntegrationConfigsTable">
        <Table
          rowKey="id"
          dataSource={integrationConfigs}
          columns={this.columns}
          pagination={false}
        />
      </div>
    )
  }
}

IntegrationConfigsTable.defaultProps = {
  hasPermission: false
}

export default IntegrationConfigsTable
