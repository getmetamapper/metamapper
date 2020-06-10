import gql from "graphql-tag"

export default gql`
  mutation revokeMembership($email: String!) {
    revokeMembership(input: { email: $email }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
