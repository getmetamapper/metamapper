import React, { Component } from "react"
import { compose } from "react-apollo"
import { Button, Col, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import Link from "app/Navigation/Link"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import ChecksTable from "app/Datastores/DatastoreChecks/ChecksTable"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetDatastoreChecks from "graphql/withGetDatastoreChecks"

class DatastoreChecks extends Component {
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
        label: "Checks",
      },
    ]
  }

  render() {
    const {
      checks,
      datastore,
      loading,
    } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Checks - ${datastore.slug} - Metamapper`}
        hideSchemaSelector
      >
        <Row>
          <Col span={22} offset={1}>
            <Row className="datastore-checks-header">
              <Col span={16}>
                <h2>Checks</h2>
              </Col>
              <Col span={8} style={{ textAlign: "right" }}>
                <Link to={`/datastores/${datastore.slug}/checks/new`} data-test="NewCheckButton">
                  <Button type="primary">Create New Check</Button>
                </Link>
              </Col>
            </Row>
            <Row>
              <Col span={24}>
                <ChecksTable
                  checks={checks}
                  datastore={datastore}
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
  withGetDatastoreChecks,
  withLargeLoader,
  withNotFound,
)(DatastoreChecks)
