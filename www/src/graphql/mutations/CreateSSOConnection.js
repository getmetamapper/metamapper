import gql from "graphql-tag"

export default gql`
  mutation CreateSSOConnection(
    $id: String!
    $provider: String!
    $entityId: String!
    $defaultPermissions: String!
    $ssoUrl: String
    $x509cert: String
    $extras: JSONObject
  ) {
    createSSOConnection(
      input: {
        id: $id
        provider: $provider
        entityId: $entityId
        defaultPermissions: $defaultPermissions
        ssoUrl: $ssoUrl
        x509cert: $x509cert
        extras: $extras
      }
    ) {
      ssoConnection {
        id
        pk
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
