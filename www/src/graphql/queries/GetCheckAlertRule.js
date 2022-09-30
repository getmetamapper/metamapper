import gql from "graphql-tag"

export default gql`
query GetCheckAlertRule(
  $id: ID!
) {
  checkAlertRule(id: $id) {
    id
    name
    interval {
      label
      value
    }
    channel
    channelConfig
  }
}
`
