import gql from "graphql-tag"

export default gql`
  mutation UpdateDatastoreDescription($id: ID!, $shortDesc: String) {
    updateDatastoreMetadata(input: { id: $id, shortDesc: $shortDesc }) {
      datastore {
        id
        slug
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
