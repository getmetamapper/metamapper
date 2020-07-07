import gql from "graphql-tag"

export default gql`
  mutation ToggleDatastoreObjectPermissions(
    $id: ID!
  ) {
    toggleDatastoreObjectPermissions(
      input: {
        id: $id
      }
    ) {
      isEnabled
      errors {
        resource
        field
        code
      }
    }
  }
`
