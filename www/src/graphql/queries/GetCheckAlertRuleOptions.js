import gql from "graphql-tag"

export default gql`
query GetCheckAlertRuleOptions {
  intervalOptions: checkIntervalOptions {
    label
    value
  }
  channelOptions: checkAlertChannels {
    label
    value
  }
}
`
