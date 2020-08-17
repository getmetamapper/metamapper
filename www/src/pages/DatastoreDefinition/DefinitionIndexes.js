import React, { Component } from "react"
import { compose } from "react-apollo"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import IndexDefinitionTable from "app/Datastores/DatastoreDefinition/IndexDefinitionTable"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableIndexes from "graphql/withGetTableIndexes"

class DatastoreIndexes extends Component {
  state = { columnDetailsVisible: false, selectedColumn: null }

  handleOpenDetails = (selectedColumn) => {
    this.setState({
      selectedColumn,
      columnDetailsVisible: true,
    })
  }

  handleCloseDetails = () => {
    this.setState({ columnDetailsVisible: false })
  }

  render() {
    const {
      datastore,
      tableDefinition,
      tableIndexes,
      loading,
    } = this.props
    return (
      <Layout
        datastore={datastore}
        lastCrumb="Indexes"
        loading={loading}
        table={tableDefinition}
      >
        <IndexDefinitionTable dataSource={tableIndexes} loading={loading} />
      </Layout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ tableDefinition }) => {
  return !tableDefinition || !tableDefinition.hasOwnProperty("id")
})

export default compose(
  withGetDatastoreDefinition,
  withGetTableIndexes,
  withLargeLoader,
  withNotFound,
)(DatastoreIndexes)
