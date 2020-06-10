import gql from "graphql-tag"

export default gql`
  mutation ResetPassword($email: String!) {
    resetPassword(email: $email) {
      ok
    }
  }
`
