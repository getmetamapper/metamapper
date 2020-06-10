import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { Row, Col, Input } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from 'hoc/withNotFoundHandler'

class Omnisearch extends Component {
  handleSearch = (value) => {
    const {
      currentWorkspace: { slug },
    } = this.props

    this.props.history.push(`/${slug}/search/results?q=${value}`)
  }

  render() {
    const { currentWorkspace } = this.props
    return (
      <Row className="omnisearch">
        <Helmet>
          <title>Search Your Data – {currentWorkspace.slug} – Metamapper</title>
        </Helmet>
        <Col span={8} offset={8}>
          <div className="omnisearch-title">
            <h1 className="text-centered">Metamapper</h1>
            <p className="omnisearch-tagline">
              The search engine for your data.
            </p>
          </div>
          <div className="omnisearch-box">
            <Input.Search
              block
              size="large"
              onSearch={this.handleSearch}
              data-test="Omnisearch.Searchbox"
            />
          </div>
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
  withUserContext,
  withLargeLoader,
  withNotFound,
)(Omnisearch)
