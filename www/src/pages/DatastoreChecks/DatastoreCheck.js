import React, { Component } from "react"
import { compose } from "react-apollo"
import { Col, Divider, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { ellipsis } from "lib/utilities"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import CheckHeader from "app/Datastores/DatastoreChecks/CheckHeader"
import CheckAlertRules from "app/Datastores/DatastoreChecks/CheckAlertRules"
import CheckExecutions from "app/Datastores/DatastoreChecks/CheckExecutions"
import CheckExpectations from "app/Datastores/DatastoreChecks/CheckExpectations"
import CheckQueryText from "app/Datastores/DatastoreChecks/CheckQueryText"
import withGetCheckExpectations from "graphql/withGetCheckExpectations"
import withGetDatastoreCheck from "graphql/withGetDatastoreCheck"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withNotFoundHandler from "hoc/withNotFoundHandler"

class DatastoreCheck extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      check,
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
        to: `/${slug}/datastores/${datastoreSlug}/checks`,
      },
      {
        label: ellipsis(check.name),
      },
    ]
  }

  render() {
    const {
      check,
      expectations,
      datastore,
      loading,
    } = this.props
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`${check.name} - Checks - ${datastore.slug} - Metamapper`}
        hideSchemaSelector
      >
        <Row>
          <Col span={22} offset={1}>
            <CheckHeader
              check={check}
              datastore={datastore}
              loading={loading}
            />
            <Divider />
            <div className="check-query">
              <h2>SQL Statement</h2>
              <CheckQueryText
                hasFooter
                sqlText={check.query.sqlText}
              />
            </div>
            <CheckExpectations
              check={check}
              expectations={expectations}
              queryColumns={check.query.columns}
              loading={loading}
            />
            <CheckAlertRules
              check={check}
              loading={loading}
            />
            <CheckExecutions
              check={check}
              loading={loading}
            />
          </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ check, datastore }) => {
  return !datastore || !check || !datastore.hasOwnProperty("id") || !check.hasOwnProperty("id")
})

export default compose(
  withGetDatastoreSettings,
  withGetDatastoreCheck,
  withGetCheckExpectations,
  withLargeLoader,
  withNotFound,
)(DatastoreCheck)
