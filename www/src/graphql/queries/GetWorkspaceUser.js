import gql from "graphql-tag"

export default gql`
  query workspaceUser($userId: ID!) {
    workspaceUser(id: $userId) {
      pk
      userId
      avatarUrl
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
