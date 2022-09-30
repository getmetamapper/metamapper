import gql from "graphql-tag"

export default gql`
mutation DeleteCheckAlertRule($id: ID!) {
  deleteCheckAlertRule(input: { id: $id }) {
    ok
    errors {
      resource
      field
      code
    }
  }
}
`
