import React, { Component } from "react"
import { compose } from "react-apollo"
import { Col, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import moment from "moment"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import RunHistoryTable from "app/Datastores/RunHistory/RunHistoryTable"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetDatastoreRunHistory from "graphql/withGetDatastoreRunHistory"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class RunHistory extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    return [
      {
        label: "Datastores",
        to: `/${slug}/datastores`,
      },
      {
        label: datastoreSlug,
        to: `/${slug}/datastores/${datastoreSlug}`,
      },
      {
        label: "Run History",
      },
    ]
  }

  renderTitle = (selectedRun) => {
    let title = "Revisions"
    if (selectedRun) {
      title += ` – ${moment(selectedRun.createdOn).format("MMMM Do, YYYY")}`
    }
    return title
  }

  render() {
    const { datastore, runHistory, loading } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Run History - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={16} offset={4}>
            <RunHistoryTable runs={runHistory} />
          </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

export default compose(
  withGetDatastoreSettings,
  withGetDatastoreRunHistory,
  withLargeLoader,
  withNotFound,
)(RunHistory)
