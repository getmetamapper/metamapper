import gql from "graphql-tag"

export default gql`
  query GetDatastoreAssets(
    $datastoreSlug: String!
    $schema: String
    $after: String
    $search: String
    $orderBy: String
  ) {
    datastoreAssets(
      slug: $datastoreSlug
      schema: $schema
      search: $search
      after: $after
      first: 100
      orderBy: $orderBy
    ) {
      edges {
        node {
          id
          name
          kind
          shortDesc
          schema {
            name
          }
          usage {
            popularityScore
            totalQueries
            totalUsers
            windowInDays
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
`
