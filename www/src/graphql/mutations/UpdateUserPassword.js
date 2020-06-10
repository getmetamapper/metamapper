import gql from "graphql-tag"

export default gql`
  mutation updateUserPassword($password: String!, $currentPassword: String!) {
    updateCurrentUser(
      input: { password: $password, currentPassword: $currentPassword }
    ) {
      user {
        email
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
