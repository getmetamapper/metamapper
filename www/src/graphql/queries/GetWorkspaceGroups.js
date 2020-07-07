import gql from "graphql-tag"

export default gql`
  query getWorkspaceGroups {
    workspaceGroups {
      edges {
        node {
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
