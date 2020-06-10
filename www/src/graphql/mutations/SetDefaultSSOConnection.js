import gql from "graphql-tag"

export default gql`
  mutation SetDefaultSSOConnection($connection: String) {
    setDefaultSSOConnection(input: { connection: $connection }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
