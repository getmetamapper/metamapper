import gql from "graphql-tag"

export default gql`
  mutation UpdateColumnMetadata(
    $id: ID!
    $shortDesc: String
    $readme: String
  ) {
    updateColumnMetadata(input: { id: $id, shortDesc: $shortDesc, readme: $readme }) {
      column {
        id
        name
        shortDesc
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
