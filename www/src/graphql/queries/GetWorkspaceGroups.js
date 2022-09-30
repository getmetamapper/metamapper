import gql from "graphql-tag"

export default gql`
  query GetWorkspaceGroups {
    workspaceGroups {
      edges {
        node {
          pk
          id
          name
          description
          createdAt
          usersCount
        }
      }
      totalCount
    }
  }
`
