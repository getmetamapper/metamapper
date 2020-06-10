import gql from "graphql-tag"

export default gql`
  mutation DeleteDatastore($id: ID!) {
    deleteDatastore(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
