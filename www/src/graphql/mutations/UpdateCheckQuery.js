import gql from "graphql-tag"

export default gql`
mutation UpdateCheckQuery(
  $id: ID!
  $queryId: ID
) {
  updateCheck(input: {
    id: $id
    queryId: $queryId
  }) {
    check {
      pk
    }
    errors {
      resource
      field
      code
    }
  }
}
`
