import gql from "graphql-tag"

export default gql`
  query GetSSOConnections {
    ssoConnections {
      edges {
        node {
          pk
          id
          name
          provider
          protocol
          audience
          defaultPermissions
          entityId
          extras
          isDefault
          isEnabled
        }
      }
    }
  }
`
