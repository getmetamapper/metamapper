import gql from "graphql-tag"

export default gql`
mutation CreateCheckAlertRule(
  $id: ID!
  $name: String!
  $interval: String!
  $channel: String!
  $channelConfig: JSONObject!
) {
  createCheckAlertRule(input: {
    id: $id
    name: $name
    interval: $interval
    channel: $channel
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
