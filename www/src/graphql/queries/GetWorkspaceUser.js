import gql from "graphql-tag"

export default gql`
  query workspaceUser($userId: ID!) {
    workspaceUser(id: $userId) {
      pk
      userId
      name
      email
      createdAt
      workspaceGroups {
        id
        name
        description
      }
    }
  }
`
