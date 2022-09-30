import gql from "graphql-tag"

export default gql`
query GetCheckExecution(
  $id: ID!
) {
  checkExecution(id: $id) {
    id
    status
    error
    startedAt
    finishedAt
    executedQueryText
    expectationResults {
      epoch
      passed
      expectation {
        description
      }
      observedValue
      expectedValue
    }
  }
}
`
