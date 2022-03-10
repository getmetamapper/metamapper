import React, { Component, Fragment } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Col, Form, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import qs from "query-string"
import Layout from "app/Datastores/DatastoreLayout"
import FirstRunPending from "app/Datastores/RunHistory/FirstRunPending"
import DatastoreAssetsSearch from "app/Datastores/DatastoreAssets/DatastoreAssetsSearch"
import DatastoreAssetsTable from "app/Datastores/DatastoreAssets/DatastoreAssetsTable"
import withGetDatastoreAssets from "graphql/withGetDatastoreAssets"
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class DatastoreAssets extends Component {
  constructor(props) {
    super(props)

    this.breadcrumbs = this.breadcrumbs.bind(this)
    this.handleSearchSubmit = this.handleSearchSubmit.bind(this)
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

  handleSearchSubmit = (evt) => {
    evt.preventDefault()

    const {
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    this.props.form.validateFields((err, { search }) => {
      if (err) return

      const rootUri = `/${slug}/datastores/${datastoreSlug}/assets`
      const qParams = qs.parse(window.location.search)

      if (search) {
        this.props.history.push(`${rootUri}?${qs.stringify({ ...qParams, search })}`)
      } else {
        this.props.history.push(rootUri)
      }
    })
  }

  render() {
    const {
      assets,
      datastore,
      fetchNextPage,
      form,
      hasNextPage,
      loading,
      search,
    } = this.props
    return (
      <Layout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Datastore Assets - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={22} offset={1}>
            {datastore.firstRunIsPending ? (
              <FirstRunPending datastore={datastore} />
            ) : (
              <Fragment>
                <DatastoreAssetsSearch
                  form={form}
                  search={search}
                  onSearch={this.handleSearchSubmit}
                />
                <DatastoreAssetsTable
                  dataSource={assets}
                  hasNextPage={hasNextPage}
                  datastore={datastore}
                  loading={loading}
                  fetchNextPage={fetchNextPage}
                />
              </Fragment>
            )}
          </Col>
        </Row>
      </Layout>
    )
  }
}

const withSearchQuery = (ChildComponent) => {
  const ComposedComponent = (props) => {
    const {
      search, schema,
    } = qs.parse(window.location.search)
    return <ChildComponent search={search} schema={schema} {...props} />
  }
  return ComposedComponent
}

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

const withForm = Form.create()

export default compose(
  withRouter,
  withForm,
  withSearchQuery,
  withGetDatastoreDefinition,
  withGetDatastoreAssets,
  withLargeLoader,
  withNotFound,
)(DatastoreAssets)
