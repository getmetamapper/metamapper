import React, { Component, Fragment } from "react"
import { compose } from "react-apollo"
import { Table, Tag } from "antd"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import IntegrationInfo from "app/WorkspaceSettings/Integrations/IntegrationInfo"

class IntegrationsTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        render: (row) => <IntegrationInfo integration={row} />
      },
      {
        align: "right",
        dataIndex: "tags",
        render: (tags) => (
          <Fragment>
            {tags.map(tag => <Tag>{tag}</Tag>)}
          </Fragment>
        ),
      }
    ];
  }

  handleClick = (integration) => {
    const {
      currentWorkspace: { slug: workspaceSlug },
    } = this.props

    this.props.history.push(
      `/${workspaceSlug}/settings/integrations/${integration.id.toLowerCase()}`)
  }

  render() {
    const { integrations } = this.props
    return (
      <div className="integrations-table" data-test="IntegrationsTable">
        <Table
          rowKey="id"
          dataSource={integrations}
          columns={this.columns}
          pagination={false}
          onRow={(r) => ({ onClick: () => this.handleClick(r) })}
        />
      </div>
    )
  }
}

export default compose(
  withRouter,
  withUserContext,
)(IntegrationsTable)
