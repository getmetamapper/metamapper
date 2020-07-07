import gql from "graphql-tag"

export default gql`
  query getWorkspaceGroupUsers($groupId: ID!) {
    workspaceGroupUsers(groupId: $groupId) {
      edges {
        node {
          id
          pk
          name
          email
        }
      }
      totalCount
    }
  }
`
