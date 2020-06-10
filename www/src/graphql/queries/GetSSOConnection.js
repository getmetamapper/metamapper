import gql from "graphql-tag"

export default gql`
  query getSSOConnection($pk: String!) {
    ssoConnectionByPrimaryKey(pk: $pk) {
      id
      pk
      provider
      protocol
      entityId
      audience
      ssoUrl
      x509cert
      mappings
    }
  }
`
