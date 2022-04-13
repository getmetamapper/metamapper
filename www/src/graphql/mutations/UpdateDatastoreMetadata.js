import gql from "graphql-tag"

export default gql`
  mutation UpdateDatastoreMetadata(
    $id: ID!
    $name: String
    $tags: [String]
    $incidentContacts: [String]
    $isEnabled: Boolean
  ) {
    updateDatastoreMetadata(
      input: {
        id: $id,
        name: $name,
        tags: $tags,
        incidentContacts: $incidentContacts,
        isEnabled: $isEnabled
      }
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
