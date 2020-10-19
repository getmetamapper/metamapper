import gql from "graphql-tag"

export default gql`
  query GetColumnDefinition(
    $datastoreId: ID!
    $schemaName: String!
    $tableName: String!
    $columnName: String!
  ) {
    columnDefinition(
      datastoreId: $datastoreId
      schemaName: $schemaName
      tableName: $tableName
      columnName: $columnName
    ) {
      id
      name
      readme
    }
  }
`
