import React, { Component } from "react"
import { compose } from "react-apollo"
import { Col, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import DatastoreActivity from "app/Datastores/DatastoreOverview/DatastoreActivity"
import DatastoreDetails from "app/Datastores/DatastoreOverview/DatastoreDetails"
import UpdateCustomProperties from "app/Datastores/CustomProperties/UpdateCustomProperties"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetDatastoreCustomProperties from "graphql/withGetDatastoreCustomProperties"
import withGetRecentDatastoreActivities from "graphql/withGetRecentDatastoreActivities"

class DatastoreOverview extends Component {
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
        label: "Overview",
      },
    ]
  }

  render() {
    const {
      customProperties,
      datastore,
      loading,
      recentDatastoreActivities,
    } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Datastore Overview - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={22} offset={1}>
            <DatastoreDetails datastore={datastore} />
            <Row gutter={24}>
              <Col span={10}>
                <UpdateCustomProperties
                  contentObject={datastore}
                  contentType="DATASTORE"
                  customProperties={customProperties}
                  loading={loading}
                />
              </Col>
              <Col span={14}>
                <DatastoreActivity
                  datastore={datastore}
                  activities={recentDatastoreActivities}
                  title="Recent Activity"
                  loading={loading}
                />
              </Col>
            </Row>
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
  withGetDatastoreCustomProperties,
  withGetRecentDatastoreActivities,
  withLargeLoader,
  withNotFound,
)(DatastoreOverview)
