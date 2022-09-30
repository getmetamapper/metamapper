import gql from "graphql-tag"

export default gql`
query GetIntegration($id: String!) {
  integration(id: $id) {
    name
    info
    handler
    installed
    details {
      name
      type
      label
      options
      helpText
    }
  }
}
`
