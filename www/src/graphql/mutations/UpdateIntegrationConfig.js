import gql from "graphql-tag"

export default gql`
mutation UpdateIntegrationConfig(
  $id: ID!
  $meta: JSONObject
) {
  updateIntegrationConfig(input: {
    id: $id
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
