import gql from "graphql-tag"

export default gql`
  mutation AddUserToGroup(
    $groupId: ID!,
    $userId: ID!,
  ) {
    addUserToGroup(input: {
      id: $groupId,
      userId: $userId,
    }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
