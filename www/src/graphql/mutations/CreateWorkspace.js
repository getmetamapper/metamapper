import gql from "graphql-tag"

export default gql`
  mutation CreateWorkspace($name: String!, $slug: String!) {
    createWorkspace(input: { name: $name, slug: $slug }) {
      workspace {
        id
        pk
        name
        slug
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
