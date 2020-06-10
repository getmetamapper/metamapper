import gql from "graphql-tag"

export default gql`
  query getTableIndexes(
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
      indexes {
        edges {
          node {
            id
            name
            sql
            isPrimary
            isUnique
            columns {
              name
            }
            createdAt
          }
        }
      }
    }
  }
`
