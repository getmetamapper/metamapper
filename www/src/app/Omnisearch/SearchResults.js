import React from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { List, Divider, Row, Col } from "antd"
import { mapKeys } from "lodash"
import SearchResultItem from "app/Omnisearch/SearchResultItem"
import withLoader from "hoc/withLoader"
import withGetOmnisearchResults from "graphql/withGetOmnisearchResults"

const SearchResults = ({ datastores, searchResults, timeElapsed }) => {
  const datastoreMap = mapKeys(datastores, "pk")
  return (
    <span data-test="SearchResults">
      <Row>
        <Col span={12}>
          <span className="omnisearch-results-title">
            <h3>Search Results</h3>
          </span>
        </Col>
        <Col span={12}>
          <span className="omnisearch-results-count">
            {searchResults.length} results ({timeElapsed} seconds)
          </span>
        </Col>
      </Row>
      <Divider />
      <List
        dataSource={searchResults}
        renderItem={(item) => (
          <SearchResultItem
            datastore={datastoreMap[item.datastoreId]}
            highlightWords={["customer"]}
            {...item}
          />
        )}
      />
    </span>
  )
}

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

export default compose(
  withRouter,
  withGetOmnisearchResults,
  withLargeLoader
)(SearchResults)
