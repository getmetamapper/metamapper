import gql from "graphql-tag"

export default gql`
  query getWorkspaceUsers($workspaceId: ID!, $activeOnly: Boolean) {
    workspaceUsers(workspaceId: $workspaceId, activeOnly: $activeOnly) {
      edges {
        node {
          pk
          userId
          avatarUrl
          name
          email
          permissions
        }
      }
    }
  }
`
