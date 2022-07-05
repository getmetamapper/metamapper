import gql from "graphql-tag"

export default gql`
query GetDatastoreCheck(
  $checkId: ID!
) {
  datastoreCheck: check(id: $checkId) {
    id
    pk
    name
    isEnabled
    shortDesc
    tags
    interval {
      label
      value
    }
    creator {
      id
      name
      email
      avatarUrl
    }
    query {
      columns
      sqlText
    }
    createdAt
    updatedAt
  }
}
`
