import gql from "graphql-tag"

export default gql`
  mutation ResetPasswordConfirm(
    $password: String!
    $uid: Int!
    $token: String!
  ) {
    resetPasswordConfirm(password: $password, uid: $uid, token: $token) {
      ok
    }
  }
`
