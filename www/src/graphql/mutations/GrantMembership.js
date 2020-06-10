import gql from "graphql-tag"

export default gql`
  mutation grantMembership($email: String!, $permissions: String!) {
    grantMembership(input: { email: $email, permissions: $permissions }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
