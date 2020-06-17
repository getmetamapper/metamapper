import gql from "graphql-tag"

export default gql`
  mutation DisableDatastoreCustomFields(
    $id: ID!,
    $disabledDatastoreProperties: [String],
    $disabledTableProperties: [String],
  ) {
    disableDatastoreCustomFields(input: {
      id: $id,
      disabledDatastoreProperties: $disabledDatastoreProperties,
      disabledTableProperties: $disabledTableProperties,
    }) {
      datastore {
        id
        disabledDatastoreProperties
        disabledTableProperties
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
