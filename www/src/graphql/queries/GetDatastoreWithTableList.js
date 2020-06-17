import gql from "graphql-tag"

export default gql`
  query getDatastoreTableList($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      id
      pk
      slug
      name
      tags
      version
      isEnabled
      hasIndexes
      hasConstraints
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
