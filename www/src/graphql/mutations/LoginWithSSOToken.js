import gql from "graphql-tag"

export default gql`
  mutation LoginWithSSOToken($uid: Int!, $token: String!) {
    loginWithSSOToken(uid: $uid, token: $token) {
      jwt
    }
  }
`
