import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { compose } from "react-apollo"
import { map, filter, uniqBy } from "lodash"
import { Button, Card, Col, Form, Row } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { withRouter } from "react-router-dom"
import qs from "query-string"
import SearchResults from "app/Omnisearch/SearchResults"
import withGetDatastoreFacet from "graphql/withGetDatastoreFacet"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import FacetCheckboxWidget from "app/Omnisearch/FacetCheckboxWidget"
import withGetOmnisearchResults from "graphql/withGetOmnisearchResults"

class OmnisearchResults extends Component {
  constructor(props) {
    super(props)

    const { q: query } = qs.parse(props.location.search)

    this.state = {
      query,
    }

    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleSubmit = () => {
    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        pathname,
        search,
      } = this.props.location

      this.props.history.push(`${pathname}?${qs.stringify({ ...qs.parse(search), ...variables })}`)
    })
  }

  handleClear = () => {
    this.props.history.push(`${this.props.location.pathname}?q=${this.state.query}`)
  }

  getDatastores = () => {
    const buckets = map(this.props.facets.datastores.buckets, 'key')
    return map(
      filter(
        this.props.datastores, ({ pk }) => buckets.indexOf(pk) > -1
      ),
      ({ pk, name }) => ({ label: name, value: pk }),
    )
  }

  getEngines = () => {
    const buckets = map(this.props.facets.datastores.buckets, 'key')
    return uniqBy(
      map(
        filter(
          this.props.datastores, ({ pk }) => buckets.indexOf(pk) > -1
        ),
        ({ engineName, jdbcConnection: { engine } }) => ({ label: engineName, value: engine })
      ),
      'value'
    )
  }

  getSchemas = () => {
    return map(
      this.props.facets.schemas.buckets,
      ({ key, doc_count }) => ({ label: key, value: key }),
    )
  }

  getTags = () => {
    return map(
      this.props.facets.tags.buckets,
      ({ key, doc_count }) => ({ label: key, value: key }),
    )
  }

  render() {
    const { datastores, form, results, elapsed } = this.props
    return (
      <Row>
        <Helmet>
          <title>{this.state.query} – Search – Metamapper</title>
        </Helmet>
        <Col span={6} offset={2} className="omnisearch-sidebar">
          <Card title="Filters" extra={
              <div className="omnisearch-sidebar-actions">
                <Button type="default" size="small" onClick={this.handleClear}>Clear</Button>
                <Button type="primary" size="small" onClick={this.handleSubmit}>Apply Changes</Button>
              </div>
          }>
            <FacetCheckboxWidget
              title="Datastores"
              form={form}
              name="datastores"
              options={this.getDatastores()}
            />
            <FacetCheckboxWidget
              title="Engines"
              form={form}
              name="engines"
              options={this.getEngines()}
            />
            <FacetCheckboxWidget
              title="Schema"
              form={form}
              name="schemas"
              options={this.getSchemas()}
            />
            <FacetCheckboxWidget
              title="Tags"
              form={form}
              name="tags"
              options={this.getTags()}
            />
          </Card>
        </Col>
        <Col span={12} offset={1} className="omnisearch-results">
          <SearchResults
            datastores={datastores}
            results={filter(results, (r) => r.searchResult !== null)}
            elapsed={elapsed}
          />
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

const withSearchForm = Form.create()

export default compose(
  withRouter,
  withSearchForm,
  withGetDatastoreFacet,
  withGetOmnisearchResults,
  withNotFound,
  withLargeLoader,
)(OmnisearchResults)
