import gql from "graphql-tag"

export default gql`
  mutation UpdateColumnMetadata($id: ID!, $shortDesc: String) {
    updateColumnMetadata(input: { id: $id, shortDesc: $shortDesc }) {
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
