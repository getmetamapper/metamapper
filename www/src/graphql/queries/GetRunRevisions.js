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
      first: 50
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
            type
            name
            label
            parentLabel
            pathname
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
