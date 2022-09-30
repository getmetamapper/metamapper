import React, { Component } from "react"
import { compose } from "react-apollo"
import { Link, withRouter } from "react-router-dom"
import { filter, map } from "lodash"
import { withUserContext } from "context/UserContext"
import { Col, Menu, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import TableDefinitionDetails from "app/Datastores/DatastoreDefinition/TableDefinitionDetails"

class DefinitionLayout extends Component {
  constructor(props) {
    super(props)

    const {
      currentWorkspace: { slug },
      match: { params },
    } = props

    const { datastoreSlug, schemaName, tableName } = params

    const baseUri = `/${slug}/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}`

    this.links = [
      {
        to: `${baseUri}/overview`,
        label: "Overview",
        visible: true,
      },
      {
        to: `${baseUri}/notes`,
        label: "Notes",
        visible: true,
      },
      {
        to: `${baseUri}/columns`,
        label: "Columns",
        visible: true,
      },
    ]

    this.links = filter(this.links, { visible: true })
    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      lastCrumb,
      currentWorkspace: { slug },
      match: { params },
    } = this.props

    const { datastoreSlug, schemaName, tableName } = params

    return [
      {
        label: "Datastores",
        to: `/${slug}/datastores`,
      },
      {
        label: datastoreSlug,
        to: `/${slug}/datastores/${datastoreSlug}`,
      },
      {
        label: "Assets",
        to: `/${slug}/datastores/${datastoreSlug}/assets`,
      },
      {
        label: schemaName,
        to: `/${slug}/datastores/${datastoreSlug}/assets?schema=${schemaName}`,
      },
      {
        label: tableName,
      },
      {
        label: lastCrumb,
      },
    ]
  }

  render() {
    const { children, datastore, table, lastCrumb, loading } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        className="datastore-definition"
        datastore={datastore}
        loading={loading}
        title={`${lastCrumb} - ${table.schema.name}.${table.name} - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={24}>
            <div>
              <TableDefinitionDetails
                datastore={datastore}
                table={table}
                schema={table.schema}
                loading={loading}
              />
              <Menu
                selectedKeys={[this.props.location.pathname]}
                mode="horizontal"
              >
                {map(this.links, ({ label, to }) => (
                  <Menu.Item key={to} data-test={`DefinitionLayout.${label}`}>
                    <Link to={to}>{label}</Link>
                  </Menu.Item>
                ))}
              </Menu>
            </div>
            <div className="datastore-definition-content">{children}</div>
          </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

export default compose(
  withRouter,
  withUserContext,
  withLargeLoader
)(DefinitionLayout)
