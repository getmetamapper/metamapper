import gql from "graphql-tag"

export default gql`
  mutation DeleteGroup(
    $id: ID!,
  ) {
    deleteGroup(input: {
      id: $id,
    }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
