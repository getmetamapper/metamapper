import gql from "graphql-tag"

export default gql`
  query GetWorkspaceGroup($groupId: ID!) {
    workspaceGroup(id: $groupId) {
      id
      pk
      name
      description
      createdAt
      usersCount
    }
  }
`
