import gql from "graphql-tag"

export default gql`
  query GetTableLastCommitTimestamp(
    $datastoreId: ID!
    $schemaName: String!
    $tableName: String!
  ) {
    tableLastCommitTimestamp(
      datastoreId: $datastoreId
      schemaName: $schemaName
      tableName: $tableName
    )
  }
`
