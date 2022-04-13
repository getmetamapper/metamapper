import gql from "graphql-tag"

export default gql`
mutation UpdateCheckAlertRule(
  $id: ID!
  $name: String
  $interval: String
  $channelConfig: JSONObject
) {
  updateCheckAlertRule(input: {
    id: $id
    name: $name
    interval: $interval
    channelConfig: $channelConfig
  }) {
    alertRule {
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
