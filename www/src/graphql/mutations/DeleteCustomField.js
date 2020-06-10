import gql from "graphql-tag"

export default gql`
  mutation DeleteCustomField($id: ID!) {
    deleteCustomField(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
