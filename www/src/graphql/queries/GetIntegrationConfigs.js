import gql from "graphql-tag"

export default gql`
query GetIntegrationConfigs($id: String!) {
  integration(id: $id) {
    id: handler
    name
    tags
    installed
    details {
      name
      label
      type
      isDisplay
      isRequired
      helpText
      options
    }
  }
  integrationConfigs(integration: $id) {
    edges {
      node {
        id
        authKeys
        displayable
        meta
        createdAt
        createdBy {
          pk
          name
          email
          avatarUrl
        }
      }
    }
  }
}
`
