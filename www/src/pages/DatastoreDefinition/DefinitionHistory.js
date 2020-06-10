import React, { Component } from "react"
import { compose } from "react-apollo"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import TableRevisionLog from "app/Datastores/Revisions/TableRevisionLog"
import withGetDatastoreWithTableList from "graphql/withGetDatastoreWithTableList"
import withGetTableDefinition from "graphql/withGetTableDefinition"
import withGetTableRevisions from "graphql/withGetTableRevisions"

class DefinitionHistory extends Component {
  state = {}

  render() {
    const {
      datastore,
      loading,
      schemas,
      tableDefinition,
      tableRevisions,
    } = this.props
    return (
      <Layout
        datastore={datastore}
        lastCrumb="History"
        loading={loading}
        schemas={schemas}
        table={tableDefinition}
      >
        <TableRevisionLog revisions={tableRevisions} />
      </Layout>
    )
  }
}

const enhance = compose(
  withGetDatastoreWithTableList,
  withGetTableDefinition,
  withGetTableRevisions
)

export default enhance(DefinitionHistory)
