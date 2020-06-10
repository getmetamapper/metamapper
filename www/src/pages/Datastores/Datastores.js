import React, { Component } from "react"
import { compose } from "react-apollo"
import { Helmet } from "react-helmet"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { Button, Col, Form, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import qs from "query-string"
import Link from "app/Navigation/Link"
import DatastoreList from "app/Datastores/DatastoreList"
import DatastoreListSearch from "app/Datastores/DatastoreListSearch"
import withGetDatastoresList from "graphql/withGetDatastoresList"

class Datastores extends Component {
  handleSearchSubmit = (evt) => {
    evt.preventDefault()

    const {
      currentWorkspace: { slug },
    } = this.props

    this.props.form.validateFields((err, { search }) => {
      if (err) return

      if (search) {
        this.props.history.push(`/${slug}/datastores?search=${search}`)
      }
    })
  }

  render() {
    const { search } = qs.parse(window.location.search)
    const { currentWorkspace, datastores, form, loading } = this.props
    return (
      <Row className="datastores-list">
        <Helmet>
          <title>Datastores - {currentWorkspace.slug} - Metamapper</title>
        </Helmet>
        <Col span={12} offset={6}>
          <Row className="searchbar">
            <Col span={16}>
              <DatastoreListSearch
                form={form}
                search={search}
                onSearch={this.handleSearchSubmit}
              />
            </Col>
            <Col span={8}>
              <Link to="/datastores/new" data-test="NewDatastoreButton">
                <Button type="primary">New Datastore</Button>
              </Link>
            </Col>
          </Row>
          <Row>
            <Col span={24}>
              <DatastoreList datastores={datastores} loading={loading} />
            </Col>
          </Row>
        </Col>
      </Row>
    )
  }
}

const withForm = Form.create()

const withNotFound = withNotFoundHandler(({
  currentWorkspace,
  match: { params },
}) => {
  return currentWorkspace.slug !== params.workspaceSlug
})

const enhance = compose(
  withForm,
  withRouter,
  withUserContext,
  withGetDatastoresList,
  withLargeLoader,
  withNotFound,
)

export default enhance(Datastores)
