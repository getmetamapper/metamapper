import gql from "graphql-tag"

export default gql`
  query GetTableDefinition(
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
      readme
      tags
      schema {
        name
      }
      usage {
        popularityScore
        totalQueries
        totalUsers
        windowInDays
      }
    }
  }
`
