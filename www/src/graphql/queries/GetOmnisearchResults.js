import gql from "graphql-tag"

export default gql`
query getSearchResults($content: String!, $datastoreId: String) {
  omnisearch(content: $content, datastoreId: $datastoreId) {
    searchResults {
      pk
      score
      modelName
      datastoreId
      searchResult {
        label
        description
        pathname
      }
    }
    timeElapsed
  }
}
`
