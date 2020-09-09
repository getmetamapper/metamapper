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
            type
            name
            label
            parentLabel
            pathname
          }
        }
      }
    }
  }
`
