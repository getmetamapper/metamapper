import gql from "graphql-tag"

export default gql`
mutation QueueRevisionerRun(
  $datastoreId: ID!,
) {
  queueRevisionerRun(datastoreId: $datastoreId) {
    ok
    errors {
      resource
      field
      code
    }
  }
}
`
