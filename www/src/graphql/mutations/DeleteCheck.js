import gql from "graphql-tag"

export default gql`
mutation DeleteCheck($id: ID!) {
  deleteCheck(input: { id: $id }) {
    ok
    errors {
      resource
      field
      code
    }
  }
}
`
