import gql from "graphql-tag"

export default gql`
  query GetDatastoreAssets($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      id
      pk
      slug
      name
      tags
      version
      isEnabled
      hasIndexes
      jdbcConnection {
        engine
      }
      schemas {
        pk
        name
        tables {
          id
          name
          kind
          shortDesc
        }
      }
      firstRunIsPending
      latestRun {
        createdOn
        finishedAt
      }
    }
  }
`
