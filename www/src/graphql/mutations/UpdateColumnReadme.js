import gql from "graphql-tag"

export default gql`
  mutation UpdateColumnReadme(
    $id: ID!
    $readme: String
  ) {
    updateColumnMetadata(input: { id: $id, readme: $readme }) {
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
