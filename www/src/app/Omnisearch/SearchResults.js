import React from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { List, Card } from "antd"
import { mapKeys } from "lodash"
import { withLargeLoader } from "hoc/withLoader"
import SearchResultItem from "app/Omnisearch/SearchResultItem"
import SearchEntityNavigator from "app/Omnisearch/SearchEntityNavigator"

const SearchResults = ({ datastores, results, elapsed }) => {
  const datastoreMap = mapKeys(datastores, "pk")
  return (
    <Card title="Search Results" extra={
      <span className="omnisearch-results-count">
        {results.length} results ({elapsed} seconds)
      </span>
    }>
      <SearchEntityNavigator />
      <List
        dataSource={results}
        renderItem={(item) => (
          <SearchResultItem
            datastore={datastoreMap[item.datastoreId]}
            {...item}
          />
        )}
      />
    </Card>
  )
}

export default compose(
  withRouter,
  withLargeLoader
)(SearchResults)
