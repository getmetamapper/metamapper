import gql from "graphql-tag"

export default gql`
  mutation UpdateTableMetadata(
    $id: ID!
    $tags: [String]
    $shortDesc: String
    $readme: String
  ) {
    updateTableMetadata(
      input: { id: $id, tags: $tags, shortDesc: $shortDesc, readme: $readme }
    ) {
      table {
        id
        name
        tags
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
