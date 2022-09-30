import gql from "graphql-tag"

export default gql`
query GetAvailableIntegrations {
  availableIntegrations {
    id: handler
    name
    installed
    tags
  }
}
`
