import gql from "graphql-tag"

export default gql`
  query workspaceGroup($groupId: ID!) {
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
