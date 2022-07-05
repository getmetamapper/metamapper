import gql from "graphql-tag"

export default gql`
  query GetTableColumns(
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
      tags
      properties
      shortDesc
      schema {
        name
      }
      usage {
        popularityScore
        totalQueries
        totalUsers
        windowInDays
      }
      columns {
        edges {
          node {
            id
            name
            objectId
            ordinalPosition
            fullDataType
            isNullable
            isPrimary
            defaultValue
            dbComment
            shortDesc
            commentsCount
            readme
          }
        }
      }
    }
  }
`
