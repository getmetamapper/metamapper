import gql from "graphql-tag"

export default gql`
  query GetWorkspaceGroupUsers($groupId: ID!) {
    workspaceGroupUsers(groupId: $groupId) {
      edges {
        node {
          id
          pk
          name
          email
          avatarUrl
        }
      }
      totalCount
    }
  }
`
