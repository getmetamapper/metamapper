import gql from "graphql-tag"

export default gql`
  mutation RemoveUserFromGroup(
    $groupId: ID!,
    $userId: ID!,
  ) {
    removeUserFromGroup(input: {
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
