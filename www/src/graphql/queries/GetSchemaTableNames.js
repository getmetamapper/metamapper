import gql from "graphql-tag"

export default gql`
  query GetSchemaTableNames(
    $datastoreId: ID!
    $schemaName: String!
  ) {
    tableNamesBySchema(datastoreId: $datastoreId, schemaName: $schemaName)
  }
`
