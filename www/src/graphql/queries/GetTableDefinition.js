import gql from "graphql-tag"

export default gql`
  query getTableDefinition(
    $datastoreId: ID!
    $schemaName: String!
    $tableName: String!
  ) {
    tableDefinition(
      datastoreId: $datastoreId
      schemaName: $schemaName
      tableName: $tableName
    ) {
      id
      name
      properties
      shortDesc
      tags
      schema {
        name
      }
    }
  }
`
