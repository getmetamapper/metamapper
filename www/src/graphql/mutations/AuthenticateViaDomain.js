import gql from "graphql-tag"

export default gql`
  mutation AuthenticateUser($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
    }
  }
`
