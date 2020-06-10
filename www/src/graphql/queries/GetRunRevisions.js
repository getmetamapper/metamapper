import gql from "graphql-tag"

export default gql`
  query getRunRevisions($runId: ID!) {
    runRevisions(runId: $runId) {
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
    }
  }
`
