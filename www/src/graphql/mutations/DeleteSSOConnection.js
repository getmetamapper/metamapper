import gql from "graphql-tag"

export default gql`
  mutation DeleteSSOConnection($id: ID!) {
    removeSSOConnection(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
