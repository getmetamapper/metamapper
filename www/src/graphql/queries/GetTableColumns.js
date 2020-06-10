import gql from "graphql-tag"

export default gql`
  query getTableColumns(
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
      columns {
        edges {
          node {
            id
            pk
            name
            objectId
            ordinalPosition
            fullDataType
            isNullable
            isPrimary
            defaultValue
            shortDesc
            commentsCount
          }
        }
      }
    }
  }
`
