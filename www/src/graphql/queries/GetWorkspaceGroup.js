import gql from "graphql-tag"

export default gql`
  query workspaceGroup($id: ID!) {
    workspaceGroup(id: $id) {
      name
      description
      createdAt
      users {
        edges {
          node {
            name
            userId
            email
          }
        }
      }
    }
  }
`
