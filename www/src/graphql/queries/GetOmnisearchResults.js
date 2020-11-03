import gql from "graphql-tag"

export default gql`
query GetSearchResults(
  $content: String!
  $types: [String]
  $datastores: [String]
  $engines: [String]
  $schemas: [String]
  $tags: [String]
) {
  omnisearch(
    content: $content
    types: $types
    datastores: $datastores
    engines: $engines
    schemas: $schemas
    tags: $tags
  ) {
    facets
    results {
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
    elapsed
  }
}
`
