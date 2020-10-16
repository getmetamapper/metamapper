import React, { Component } from "react"
import { compose } from "react-apollo"
import { Card, Col, Row } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableDefinition from "graphql/withGetTableDefinition"

class DefinitionDiscussions extends Component {
  state = {}

  render() {
    const {
      datastore,
      hasPermission,
      loading,
      tableDefinition,
    } = this.props
    return (
      <Layout
        datastore={datastore}
        lastCrumb="Overview"
        loading={loading}
        table={tableDefinition}
      >
        Test
      </Layout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ tableDefinition }) => {
  return !tableDefinition || !tableDefinition.hasOwnProperty("id")
})

const enhance = compose(
  withWriteAccess,
  withGetDatastoreDefinition,
  withGetTableDefinition,
  withLargeLoader,
  withNotFound,
)

export default enhance(DefinitionDiscussions)
