import gql from "graphql-tag"

export default gql`
mutation AccountSetup(
  $fname: String!
  $lname: String!
  $email: String!
  $password: String!
  $workspaceName: String!
  $workspaceSlug: String!
  $beaconConsent: Boolean
) {
  accountSetup(
    input: {
      fname: $fname
      lname: $lname
      email: $email
      password: $password
      workspaceName: $workspaceName
      workspaceSlug: $workspaceSlug
      beaconConsent: $beaconConsent
    }
  ) {
    jwt
    workspaceSlug
    errors {
      resource
      field
      code
    }
  }
}
`
