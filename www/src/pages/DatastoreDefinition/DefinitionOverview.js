import React, { Component } from "react"
import { compose } from "react-apollo"
import { Card, Col, Row } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreWithTableList from "graphql/withGetDatastoreWithTableList"
import withGetTableDefinition from "graphql/withGetTableDefinition"
import withGetTableCustomProperties from "graphql/withGetTableCustomProperties"
import UpdateCustomProperties from "app/Datastores/CustomProperties/UpdateCustomProperties"
import CreateComment from "app/Comments/CreateComment"
import CommentThread from "app/Comments/CommentThread"

class DefinitionOverview extends Component {
  state = {}

  render() {
    const {
      customProperties,
      datastore,
      hasPermission,
      loading,
      schemas,
      tableDefinition,
    } = this.props
    return (
      <Layout
        datastore={datastore}
        lastCrumb="Overview"
        loading={loading}
        schemas={schemas}
        table={tableDefinition}
      >
        <Row gutter={[16, 16]} style={{ padding: 16 }}>
          <Col span={10}>
            <UpdateCustomProperties
              contentObject={tableDefinition}
              contentType="TABLE"
              customProperties={customProperties}
              loading={loading}
            />
          </Col>
          <Col span={14}>
            <Card className="comments">
              <CreateComment
                parentId={null}
                contentObject={tableDefinition}
                loading={loading}
                hasPermission={hasPermission}
              />
              <CommentThread
                contentType="TABLE"
                contentObject={tableDefinition}
                loading={loading}
              />
            </Card>
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
  withGetDatastoreWithTableList,
  withGetTableDefinition,
  withGetTableCustomProperties,
  withLargeLoader,
  withNotFound,
)

export default enhance(DefinitionOverview)
