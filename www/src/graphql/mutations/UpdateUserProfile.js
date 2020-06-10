import gql from "graphql-tag"

export default gql`
  mutation updateUserProfile(
    $fname: String
    $lname: String
    $email: String
    $currentPassword: String!
  ) {
    updateCurrentUser(
      input: {
        fname: $fname
        lname: $lname
        email: $email
        currentPassword: $currentPassword
      }
    ) {
      user {
        fname
        lname
        email
      }
      jwt
      errors {
        resource
        field
        code
      }
    }
  }
`
