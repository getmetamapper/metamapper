import gql from "graphql-tag"

export default gql`
  mutation DeleteSSODomain($id: ID!) {
    removeSSODomain(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
