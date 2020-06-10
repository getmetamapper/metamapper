import gql from "graphql-tag"

export default gql`
  mutation UpdateSSOConnection(
    $id: ID!
    $entityId: String
    $ssoUrl: String
    $extras: JSONObject
    $x509cert: String
    $defaultPermissions: String
  ) {
    updateSSOConnection(
      input: {
        id: $id
        entityId: $entityId
        ssoUrl: $ssoUrl
        extras: $extras
        x509cert: $x509cert
        defaultPermissions: $defaultPermissions
      }
    ) {
      ssoConnection {
        id
        pk
        name
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
