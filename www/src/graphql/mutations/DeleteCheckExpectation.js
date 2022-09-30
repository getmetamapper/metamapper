import gql from "graphql-tag"

export default gql`
mutation DeleteCheckExpectation($id: ID!) {
  deleteCheckExpectation(input: { id: $id }) {
    ok
    errors {
      resource
      field
      code
    }
  }
}
`
