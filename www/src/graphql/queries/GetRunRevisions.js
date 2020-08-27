import gql from "graphql-tag"

export default gql`
  query GetRunRevisions(
    $runId: ID!
    $types: [String]
    $actions: [String]
    $search: String
    $after: String
  ) {
    runRevisions(
      runId: $runId
      types: $types
      actions: $actions
      search: $search
      first: 100
      after: $after
    ) {
      edges {
        node {
          id
          action
          metadata
          appliedOn
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
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
`
