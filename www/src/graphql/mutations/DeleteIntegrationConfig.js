import gql from "graphql-tag"

export default gql`
mutation DeleteIntegrationConfig($id: ID!) {
  deleteIntegrationConfig(input: { id: $id }) {
    ok
    errors {
      resource
      field
      code
    }
  }
}
`
