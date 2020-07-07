import gql from "graphql-tag"

export default gql`
  mutation createGroup(
    $name: String!,
    $description: String,
  ) {
    createGroup(input: {
      name: $name,
      description: $description,
    }) {
      group {
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
