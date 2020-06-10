import gql from "graphql-tag"

export default gql`
  mutation RegisterUser(
    $fname: String!
    $lname: String!
    $email: String!
    $password: String!
  ) {
    registerUser(
      input: {
        fname: $fname
        lname: $lname
        email: $email
        password: $password
      }
    ) {
      user {
        fname
        lname
        email
      }
      errors {
        resource
        field
        code
      }
      jwt
    }
  }
`
