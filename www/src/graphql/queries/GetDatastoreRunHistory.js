import gql from "graphql-tag"

export default gql`
  query getDatastoreRunHistory($datastoreId: ID!) {
    runHistory(datastoreId: $datastoreId, first: 30) {
      edges {
        node {
          id
          pk
          status
          createdOn
          startedAt
          finishedAt
          revisionCount
          error {
            excMessage
          }
        }
      }
    }
  }
`
