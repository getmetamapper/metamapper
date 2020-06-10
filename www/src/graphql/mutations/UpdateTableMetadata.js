import gql from "graphql-tag"

export default gql`
  mutation UpdateTableMetadata($id: ID!, $tags: [String], $shortDesc: String) {
    updateTableMetadata(
      input: { id: $id, tags: $tags, shortDesc: $shortDesc }
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
