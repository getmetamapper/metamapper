import gql from "graphql-tag"

export default gql`
mutation PreviewCheckQuery(
  $datastoreId: ID!
  $interval: String!
  $sqlText: String!
) {
  previewCheckQuery(
    input: {
      id: $datastoreId,
      interval: $interval
      sqlText: $sqlText
    }
  ) {
    query {
      id
      columns
    }
    queryResults
    sqlException
    errors {
      resource
      field
      code
    }
  }
}
`
