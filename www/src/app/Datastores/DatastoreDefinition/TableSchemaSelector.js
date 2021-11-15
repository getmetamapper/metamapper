import React, { Component, Fragment, useState } from "react"
import { Collapse, Icon, Tooltip, Input, Spin } from "antd"
import { compose } from "react-apollo"
import { map } from "lodash"
import Link from "app/Navigation/Link"
import { withRouter } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import withGetDatastoreSchemaNames from "graphql/withGetDatastoreSchemaNames"
import withGetSchemaTableNames from "graphql/withGetSchemaTableNames"
import withGetDatastoreAssets from "graphql/withGetDatastoreAssets"


const TableSchemaSelectorTables = ({ schemaTableNames, currentTable, datastore, schemaName }) => (
  <Fragment>
    {map(schemaTableNames, (tableName) => (
      <Link
        className={`tablename ${
          currentTable && currentTable.name === tableName ? "active" : ""
        }`}
        key={tableName}
        title={tableName}
        to={`/datastores/${datastore.slug}/definition/${schemaName}/${tableName}/overview`}
      >
        <Icon type="table" /> {tableName}
      </Link>
    ))}
  </Fragment>
)

const TableSchemaSelectorBasicResults = compose(
  withGetSchemaTableNames,
  withLargeLoader,
)(TableSchemaSelectorTables)

const TableSchemaSelectorBasicComponent = ({
  currentTable,
  datastore,
  onChange,
  schemas,
  loading,
}) => {
  const [activeSchemas, setActiveSchemas] = useState()
  return (
    <div className="table-schema-selector">
      {loading ? (
        <div className="loading">
          <Spin />
        </div>
      ) : (
        <Collapse
          defaultActiveKey={[currentTable.name]}
          activeKey={activeSchemas}
          onChange={setActiveSchemas}
        >
          {map(schemas, (schema) => (
            <Collapse.Panel
              key={schema}
              header={
                <Tooltip title={schema} placement="left">
                  {schema}
                </Tooltip>
              }
            >
              <TableSchemaSelectorBasicResults
                currentTable={currentTable}
                datastore={datastore}
                loading={loading}
                schemaName={schema}
              />
            </Collapse.Panel>
          ))}
        </Collapse>
      )}
      <div className="table-schema-selector-clearfix"></div>
    </div>
  )
}

const TableSchemaSelectorSearchResults = ({
  currentTable,
  datastore,
  assets,
  loading,
}) => {
  return (
    <div className="table-schema-selector search">
      {loading ? (
        <div className="loading">
          <Spin />
        </div>
      ) : (
        <Fragment>
          {map(assets, (asset) => (
            <div className="search-result">
              <Link
                className={`tablename ${
                  currentTable && currentTable.name === asset.name ? "active" : ""
                }`}
                key={`${asset.schema.name}.${asset.name}`}
                title={`${asset.schema.name}.${asset.name}`}
                to={`/datastores/${datastore.slug}/definition/${asset.schema.name}/${asset.name}/overview`}
              >
                <Icon type="table" /> {asset.schema.name}.{asset.name}
              </Link>
            </div>
          ))}
        </Fragment>
      )}
    </div>
  )
}

const TableSchemaSelectorSearchComponent = compose(
  withRouter,
  withGetDatastoreAssets,
  withLargeLoader,
)(TableSchemaSelectorSearchResults)


class TableSchemaSelectorContainer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      search: "",
    }
  }

  handleSearch = (evt) => {
    this.setState({
      search: evt.target.value,
    })
  }

  render() {
    const {
      currentTable,
      datastore,
      datastoreSchemaNames,
      loading,
    } = this.props
    const { search } = this.state
    const SidebarComponent = (search.length > 0) ? TableSchemaSelectorSearchComponent : TableSchemaSelectorBasicComponent
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
        <SidebarComponent
          currentTable={currentTable}
          datastore={datastore}
          loading={loading}
          schemas={datastoreSchemaNames}
          search={search}
        />
      </Fragment>
    )
  }
}

export default compose(withRouter, withGetDatastoreSchemaNames, withLargeLoader)(TableSchemaSelectorContainer)
