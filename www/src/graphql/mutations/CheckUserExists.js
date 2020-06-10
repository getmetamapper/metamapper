import gql from "graphql-tag"

export default gql`
  mutation CheckUserExists($email: String!) {
    userExistsCheck(email: $email) {
      ok
      email
      isSSOForced
      workspaceSlug
    }
  }
`
