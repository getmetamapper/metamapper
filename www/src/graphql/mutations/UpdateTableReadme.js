import gql from "graphql-tag"

export default gql`
  mutation UdateTableReadme(
    $id: ID!
    $readme: String
  ) {
    updateTableMetadata(
      input: { id: $id, readme: $readme }
    ) {
      table {
        id
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
