import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { find } from "lodash"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import qs from "query-string"
import ColumnDefinitionTable from "app/Datastores/DatastoreDefinition/ColumnDefinitionTable"
import ColumnDefinitionDetails from "app/Datastores/DatastoreDefinition/ColumnDefinitionDetails"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableColumns from "graphql/withGetTableColumns"

class DatastoreColumns extends Component {
  constructor(props) {
    super(props)

    this.state = {
      columnDetailsVisible: false,
      selectedColumn: null,
    }
  }

  handleOpenDetails = (selectedColumn) => {
    const {
      location: { pathname },
    } = this.props

    this.setState({
      selectedColumn,
      columnDetailsVisible: true,
    })

    window.history.pushState(
      null,
      "",
      `${pathname}?selectedColumn=${selectedColumn.id}`
    )
  }


  handleCloseDetails = () => {
    const {
      location: { pathname },
    } = this.props

    this.setState({
      columnDetailsVisible: false,
    })

    window.history.pushState(null, "", pathname)
  }

  componentDidMount = () => {
    const {
      tableColumns,
      location: { search },
    } = this.props

    const { selectedColumn } = qs.parse(search)
    const column = find(tableColumns, { id: selectedColumn })

    if (selectedColumn && column) {
      this.handleOpenDetails(column)
    }
  }

  render() {
    const {
      datastore,
      loading,
      tableColumns,
      tableDefinition,
    } = this.props
    const {
      columnDetailsVisible,
      selectedColumn,
    } = this.state
    return (
      <Layout
        datastore={datastore}
        lastCrumb="Columns"
        loading={loading}
        table={tableDefinition}
      >
        <ColumnDefinitionTable
          dataSource={tableColumns}
          loading={loading}
          onOpenDetails={this.handleOpenDetails}
        />
        <>
          {selectedColumn && (
            <ColumnDefinitionDetails
              table={tableDefinition}
              column={selectedColumn}
              visible={columnDetailsVisible}
              onClose={this.handleCloseDetails}
              loading={loading}
            />
          )}
        </>
      </Layout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ tableDefinition }) => {
  return !tableDefinition || !tableDefinition.hasOwnProperty("id")
})

const enhance = compose(
  withRouter,
  withGetDatastoreDefinition,
  withGetTableColumns,
  withLargeLoader,
  withNotFound,
)

export default enhance(DatastoreColumns)
