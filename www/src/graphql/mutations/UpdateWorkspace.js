import gql from "graphql-tag"

export default gql`
  mutation updateWorkspace(
    $id: ID!
    $name: String
    $slug: String
  ) {
    updateWorkspace(
      input: { id: $id, name: $name, slug: $slug }
    ) {
      workspace {
        id
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
