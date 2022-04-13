import gql from "graphql-tag"

export default gql`
query GetCheckAlertRules(
  $checkId: ID!
) {
  checkAlertRules(checkId: $checkId) {
    edges {
      node {
        id
        pk
        name
        channel
        channelConfig
        createdAt
        lastFailure {
          id
          finishedAt
        }
      }
    }
  }
}
`
