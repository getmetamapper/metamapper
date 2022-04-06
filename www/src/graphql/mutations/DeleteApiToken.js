import gql from "graphql-tag"

export default gql`
  mutation DeleteApiToken($id: ID!) {
    deleteApiToken(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
