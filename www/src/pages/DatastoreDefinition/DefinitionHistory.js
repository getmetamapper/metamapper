import React, { Component } from "react"
import { compose } from "react-apollo"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import TableRevisionLog from "app/Datastores/Revisions/TableRevisionLog"
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableDefinition from "graphql/withGetTableDefinition"
import withGetTableRevisions from "graphql/withGetTableRevisions"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class DefinitionHistory extends Component {
  state = {}

  render() {
    const {
      datastore,
      loading,
      tableDefinition,
      tableRevisions,
    } = this.props
    return (
      <Layout
        datastore={datastore}
        lastCrumb="History"
        loading={loading}
        table={tableDefinition}
      >
        <TableRevisionLog revisions={tableRevisions} />
      </Layout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ tableDefinition }) => {
  return !tableDefinition || !tableDefinition.hasOwnProperty("id")
})

const enhance = compose(
  withGetDatastoreDefinition,
  withGetTableDefinition,
  withGetTableRevisions,
  withLargeLoader,
  withNotFound,
)

export default enhance(DefinitionHistory)
