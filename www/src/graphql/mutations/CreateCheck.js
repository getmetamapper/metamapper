import gql from "graphql-tag"

export default gql`
mutation CreateCheck(
  $datastoreId: ID!
  $queryId: ID!
  $name: String!
  $tags: [String]
  $shortDesc: String
  $interval: String!
  $expectations: [CheckExpectation]!
) {
  createCheck(input: {
    datastoreId: $datastoreId
    queryId: $queryId
    name: $name
    tags: $tags
    shortDesc: $shortDesc
    interval: $interval
    expectations: $expectations
  }) {
    check {
      pk
    }
    errors {
      resource
      field
      code
    }
  }
}
`
