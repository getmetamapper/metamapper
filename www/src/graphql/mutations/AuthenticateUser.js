import gql from "graphql-tag"

export const queryAsString = `
  mutation AuthenticateUser($email: String!, $password: String!) {
    tokenAuth(email: $email, password: $password) {
      token
    }
  }
`

export default gql(queryAsString)
