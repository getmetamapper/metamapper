import React, { Component, Fragment } from "react"
import { Collapse, Icon, Tooltip, Input, Spin } from "antd"
import { compose } from "react-apollo"
import { map, cloneDeep } from "lodash"
import Link from "app/Navigation/Link"
import withGetTableSchemaSelector from "graphql/withGetTableSchemaSelector"
import { withRouter } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"

const TableSchemaSelectorComponent = ({
  activeSchemas,
  currentTable,
  datastore,
  onChange,
  schemas,
  loading,
}) => (
  <div className="table-schema-selector">
    {loading ? (
      <div className="loading">
        <Spin />
      </div>
    ) : (
      <Collapse
        defaultActiveKey={[currentTable.name]}
        activeKey={activeSchemas}
        onChange={onChange}
      >
        {map(schemas, ({ name: schema, tables }) => (
          <Collapse.Panel
            key={schema}
            header={
              <Tooltip title={schema} placement="left">
                {schema}
              </Tooltip>
            }
          >
            {map(tables, (table) => (
              <Link
                className={`tablename ${
                  currentTable.name === table.name ? "active" : ""
                }`}
                key={table.id}
                title={table.name}
                to={`/datastores/${datastore.slug}/definition/${schema}/${table.name}/overview`}
              >
                <Icon type="table" /> {table.name}
              </Link>
            ))}
          </Collapse.Panel>
        ))}
      </Collapse>
    )}
  </div>
)

class TableSchemaSelectorContainer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      activeSchemas: [],
      filteredSchemas: cloneDeep(props.schemas),
    }
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

  handleChange = (activeSchemas) => {
    this.setState({ activeSchemas })
  }

  render() {
    const {
      currentTable,
      datastore,
      loading,
    } = this.props
    const { activeSchemas, filteredSchemas } = this.state
    return (
      <Fragment>
        <div className="table-schema-search">
          <Input.Search
            type="text"
            placeholder="Search datastore tables"
            onChange={this.handleSearch}
            data-test="TableSchemaSearch.Input"
          />
        </div>
        <TableSchemaSelectorComponent
          activeSchemas={activeSchemas}
          currentTable={currentTable}
          datastore={datastore}
          schemas={filteredSchemas}
          onChange={this.handleChange}
          loading={loading}
        />
      </Fragment>
    )
  }
}

export default compose(withRouter, withGetTableSchemaSelector, withLargeLoader)(TableSchemaSelectorContainer)
