import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Col, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import Layout from "app/Datastores/DatastoreLayout"
import DatastoreAssetsTable from "app/Datastores/DatastoreAssets/DatastoreAssetsTable"
import withGetDatastoreAssets from "graphql/withGetDatastoreAssets"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class DatastoreAssets extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs = (datastore) => {
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
        label: "Assets",
      },
    ]
  }

  render() {
    const { datastore, schemas, loading } = this.props
    return (
      <Layout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Datastore Assets - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={20} offset={2}>
            <DatastoreAssetsTable
              datastore={datastore}
              schemas={schemas}
              loading={loading}
            />
          </Col>
        </Row>
      </Layout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

export default compose(
  withRouter,
  withGetDatastoreAssets,
  withLargeLoader,
  withNotFound,
)(DatastoreAssets)
