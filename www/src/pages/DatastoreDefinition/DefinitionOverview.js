import React, { Component } from "react"
import { compose } from "react-apollo"
import { Col, Row } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableDefinitionWithOwners from "graphql/withGetTableDefinitionWithOwners"
import withGetTableCustomProperties from "graphql/withGetTableCustomProperties"
import UpdateCustomProperties from "app/Datastores/CustomProperties/UpdateCustomProperties"
import TableReadme from "app/Datastores/DatastoreDefinition/TableReadme"
import TableOwners from "app/Datastores/DatastoreDefinition/TableOwners"

class DefinitionOverview extends Component {
  state = {}

  render() {
    const {
      customProperties,
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
        <Row gutter={[16, 16]} style={{ padding: 16 }}>
          <Col span={10}>
            <TableOwners
              tableDefinition={tableDefinition}
              loading={loading}
              hasPermission={hasPermission}
            />
            <UpdateCustomProperties
              contentObject={tableDefinition}
              contentType="TABLE"
              customProperties={customProperties}
              loading={loading}
            />
          </Col>
          <Col span={14}>
            <TableReadme
              datastore={datastore}
              tableDefinition={tableDefinition}
              loading={loading}
              hasPermission={hasPermission}
            />
          </Col>
        </Row>
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
  withGetTableDefinitionWithOwners,
  withGetTableCustomProperties,
  withLargeLoader,
  withNotFound,
)

export default enhance(DefinitionOverview)
