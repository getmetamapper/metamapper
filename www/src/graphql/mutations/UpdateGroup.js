import gql from "graphql-tag"

export default gql`
  mutation updateGroup(
    $id: ID!,
    $name: String,
    $description: String,
  ) {
    updateGroup(input: {
      id: $id,
      name: $name,
      description: $description,
    }) {
      group {
        id
        name
        description
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
