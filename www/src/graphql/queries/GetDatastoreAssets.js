import gql from "graphql-tag"

export default gql`
  query GetDatastoreAssets($datastoreSlug: String!, $search: String, $after: String) {
    datastoreAssets(
      slug: $datastoreSlug
      search: $search
      first: 100
      after: $after
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
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
`
