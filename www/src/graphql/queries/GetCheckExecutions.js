import gql from "graphql-tag"

export default gql`
query GetCheckExecutions(
  $checkId: ID!
) {
  checkExecutions(checkId: $checkId) {
    edges {
      node {
        id
        status
        failsCount
        tasksCount
        startedAt
        finishedAt
      }
    }
  }
}
`
