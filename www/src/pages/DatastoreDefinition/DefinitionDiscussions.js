import React, { Component } from "react"
import { compose } from "react-apollo"
import { Card } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreDefinition/DefinitionLayout"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetTableDefinition from "graphql/withGetTableDefinition"
import CreateComment from "app/Comments/CreateComment"
import CommentThread from "app/Comments/CommentThread"

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
        lastCrumb="Discussion"
        loading={loading}
        table={tableDefinition}
      >
        <div className="datastore-discussions">
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
        </div>
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
