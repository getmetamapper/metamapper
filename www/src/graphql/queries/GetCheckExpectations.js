import gql from "graphql-tag"

export default gql`
query GetCheckExpectations(
  $checkId: ID!
) {
  checkExpectations(checkId: $checkId) {
    edges {
      node {
        id
        description
      }
    }
  }
}
`
