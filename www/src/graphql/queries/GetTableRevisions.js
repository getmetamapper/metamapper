import gql from "graphql-tag"

export default gql`
  query getTableObjectRevisions($tableId: ID!) {
    tableRevisions(tableId: $tableId) {
      edges {
        node {
          id
          action
          metadata
          createdAt
          relatedResource {
            id
            pk
            type
            label
          }
          parentResource {
            id
            pk
            type
            label
          }
        }
      }
    }
  }
`
