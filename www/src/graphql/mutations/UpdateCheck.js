import gql from "graphql-tag"

export default gql`
mutation UpdateCheck(
  $id: ID!
  $name: String
  $tags: [String]
  $isEnabled: Boolean
  $shortDesc: String
  $interval: String
) {
  updateCheck(input: {
    id: $id
    name: $name
    tags: $tags
    isEnabled: $isEnabled
    shortDesc: $shortDesc
    interval: $interval
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
