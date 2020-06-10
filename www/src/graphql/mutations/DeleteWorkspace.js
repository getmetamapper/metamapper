import gql from "graphql-tag"

export default gql`
  mutation DeleteWorkspace($id: ID!) {
    deleteWorkspace(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
