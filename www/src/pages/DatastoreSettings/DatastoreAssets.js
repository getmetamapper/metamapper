import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Col, Row } from "antd"
import Layout from "app/Datastores/DatastoreLayout"
import DatastoreAssetsTable from "app/Datastores/DatastoreAssets/DatastoreAssetsTable"
import withGetDatastoreWithTableList from "graphql/withGetDatastoreWithTableList"

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

export default compose(
  withRouter,
  withGetDatastoreWithTableList
)(DatastoreAssets)
