import gql from "graphql-tag"

export default gql`
mutation CreateIntegrationConfig(
  $integration: String!
  $meta: JSONObject!
) {
  createIntegrationConfig(input: {
    integration: $integration
    meta: $meta
  }) {
    integrationConfig {
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
