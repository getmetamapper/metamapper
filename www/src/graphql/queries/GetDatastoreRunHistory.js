import gql from "graphql-tag"

export default gql`
  query getDatastoreRunHistory($datastoreId: ID!) {
    runHistory(datastoreId: $datastoreId) {
      edges {
        node {
          id
          pk
          status
          createdOn
          startedAt
          finishedAt
          revisionCount
        }
      }
    }
  }
`
