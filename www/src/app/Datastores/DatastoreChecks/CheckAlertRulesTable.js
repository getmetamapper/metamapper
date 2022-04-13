import React, { Component } from "react"
import { compose } from "react-apollo"
import { Button, Dropdown, Menu, Table } from "antd"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import Link from "app/Navigation/Link"
import moment from "moment"
import FromNow from "app/Common/FromNow"
import IntegrationIcon from "app/Integrations/IntegrationIcon"
import DeleteCheckAlertRule from "app/Datastores/DatastoreChecks/DeleteCheckAlertRule"

const Actions = ({ editUri, ruleId }) => (
  <Menu className="check-alert-rules-action">
    <Menu.Item>
      <Link to={editUri}>
        Edit
      </Link>
    </Menu.Item>
    <Menu.Item>
      <DeleteCheckAlertRule ruleId={ruleId} />
    </Menu.Item>
  </Menu>
)

class CheckAlertRulesTable extends Component {
  constructor(props) {
    super(props);

    const {
      match: {
        params: { datastoreSlug, checkId },
      },
    } = props

    const baseUri = `/datastores/${datastoreSlug}/checks/${checkId}`

    this.columns = [
      {
        width: 45,
        render: ({ channel }) => <IntegrationIcon integration={channel} />,
      },
      {
        title: "Alert Rule",
        align: "left",
        render: ({ pk, name, lastFailure }) => (
          <div className="alert-rule-name">
            <Link to={`${baseUri}/alerts/rules/${pk}/edit`}>
              {name}
            </Link>
            {lastFailure && (
              <span className="alert-last-failure">
                Triggered <Link to={`${baseUri}?selectedExecution=${lastFailure.id}`}><FromNow time={lastFailure.finishedAt} /></Link>
              </span>
            )}
          </div>
        )
      },
      {
        title: "Created",
        dataIndex: "createdAt",
        key: "createdAt",
        align: "right",
        render: (createdAt) => moment(createdAt).format("MMM D, YYYY"),
      },
    ]

    if (props.hasPermission) {
      this.columns.push({
        title: "Actions",
        align: "right",
        render: ({ pk, id }) => (
          <Dropdown
            trigger="click"
            placement="bottomLeft"
            overlay={<Actions editUri={`${baseUri}/alerts/rules/${pk}/edit`} ruleId={id} />}
          >
            <Button icon="ellipsis" />
          </Dropdown>
        )
      })
    }
  }

  render() {
    const { rules } = this.props
    return (
      <div className="check-alert-rules-table" data-test="CheckAlertRulesTable">
        <Table
          rowKey="id"
          dataSource={rules}
          pagination={false}
          columns={this.columns}
          locale={{ emptyText: "No alert rules found." }}
        />
      </div>
    )
  }
}

export default compose(
  withRouter,
  withWriteAccess,
)(CheckAlertRulesTable)
