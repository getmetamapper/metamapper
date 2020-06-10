import gql from "graphql-tag"

export default gql`
  mutation UpdateDatastoreMetadata(
    $id: ID!
    $name: String
    $tags: [String]
    $isEnabled: Boolean
  ) {
    updateDatastoreMetadata(
      input: { id: $id, name: $name, tags: $tags, isEnabled: $isEnabled }
    ) {
      datastore {
        id
        slug
        name
        tags
        isEnabled
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
