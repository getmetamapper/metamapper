import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Row, Col } from "antd"
import { find } from "lodash"
import qs from "query-string"
import Link from "app/Navigation/Link"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from 'hoc/withNotFoundHandler'
import withGetDatastoresList from "graphql/withGetDatastoresList"
import SearchResults from "app/Omnisearch/SearchResults"
import FilterSearchByDatastore from "app/Omnisearch/FilterSearchByDatastore"

class OmnisearchResults extends Component {
  constructor(props) {
    super(props)

    const { d: datastoreId, q: query } = qs.parse(props.location.search)

    this.state = {
      datastoreId,
      query,
    }

    this.handleSelect = this.handleSelect.bind(this)
  }

  handleSelect = (datastore) => {
    const {
      location: { pathname, search },
    } = this.props

    const params = qs.parse(search)

    if (!datastore && "d" in params) {
      delete params.d
    }

    if (datastore) {
      params.d = datastore.pk
    }

    window.location.href = `${pathname}?${qs.stringify(params)}`
  }

  render() {
    const { datastoreId, query } = this.state
    const { datastores } = this.props
    return (
      <Row>
        <Helmet>
          <title>{query} – Search – Metamapper</title>
        </Helmet>
        <Col span={4} offset={4} className="omnisearch-sidebar">
          <FilterSearchByDatastore
            selected={find(datastores, { pk: datastoreId })}
            datastores={datastores}
            onSelect={this.handleSelect}
          />
          <small>
            <Link to="/">back to search</Link>
          </small>
        </Col>
        <Col span={10} offset={1} className="omnisearch-results">
          <SearchResults datastores={datastores} />
        </Col>
      </Row>
    )
  }
}

const withNotFound = withNotFoundHandler(({
  currentWorkspace,
  match: { params },
}) => {
  return currentWorkspace.slug !== params.workspaceSlug
})

export default compose(
  withRouter,
  withGetDatastoresList,
  withNotFound,
  withLargeLoader,
)(OmnisearchResults)
