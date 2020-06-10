import React, { Component } from "react"
import { compose } from "react-apollo"
import { Link, withRouter } from "react-router-dom"
import { filter, map, cloneDeep } from "lodash"
import { withUserContext } from "context/UserContext"
import { Col, Input, Menu, Row } from "antd"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import TableSchemaSelector from "app/Datastores/DatastoreDefinition/TableSchemaSelector"
import TableDefinitionDetails from "app/Datastores/DatastoreDefinition/TableDefinitionDetails"
import withLoader from "hoc/withLoader"

class DefinitionLayout extends Component {
  constructor(props) {
    super(props)

    const {
      datastore,
      schemas,
      currentWorkspace: { slug },
      match: { params },
    } = props

    const { datastoreSlug, schemaName, tableName } = params

    const baseUri = `/${slug}/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}`

    this.links = [
      {
        to: `${baseUri}/overview`,
        label: "Overview",
        isDisplayed: true,
      },
      {
        to: `${baseUri}/columns`,
        label: "Columns",
        isDisplayed: true,
      },
      {
        to: `${baseUri}/indexes`,
        label: "Indexes",
        isDisplayed: datastore.hasIndexes,
      },
      {
        to: `${baseUri}/history`,
        label: "History",
        isDisplayed: true,
      },
    ]

    this.links = filter(this.links, { isDisplayed: true })

    this.state = {
      activeSchemas: [],
      filteredSchemas: cloneDeep(schemas),
    }

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

  handleSearch = (evt) => {
    const query = evt.target.value.toLowerCase()

    const filteredSchemas = cloneDeep(this.props.schemas)
      .map((schema) => {
        if (query) {
          if (schema.name.toLowerCase().indexOf(query) > -1) {
            return schema
          }
          const tables = schema.tables.filter((table) => {
            return table.name.toLowerCase().indexOf(query) > -1
          })
          schema.tables = tables
        }
        return schema
      })
      .filter((schema) => {
        return schema.tables.length > 0
      })

    let activeSchemas = []

    if (query) {
      activeSchemas = map(filteredSchemas, ({ name }) => name)
    }

    this.setState({ filteredSchemas, activeSchemas })
  }

  render() {
    const { children, datastore, table, lastCrumb, loading } = this.props
    const { activeSchemas, filteredSchemas } = this.state
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        className="datastore-definition"
        datastore={datastore}
        loading={loading}
        title={`${lastCrumb} - ${table.schema.name}.${table.name} - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={20}>
            <div>
              <TableDefinitionDetails
                table={table}
                schema={table.schema}
                latestRun={datastore.latestRun}
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
          <Col span={4}>
            <div className="table-schema-search">
              <Input.Search
                type="text"
                placeholder="Search datastore tables"
                onChange={this.handleSearch}
                data-test="TableSchemaSearch.Input"
              />
            </div>
            <TableSchemaSelector
              schemas={filteredSchemas}
              datastore={datastore}
              currentTable={table}
              activeKey={activeSchemas}
              onChange={(activeSchemas) => this.setState({ activeSchemas })}
            />
          </Col>
        </Row>
      </DatastoreLayout>
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

export default compose(
  withRouter,
  withUserContext,
  withLargeLoader
)(DefinitionLayout)
