import gql from "graphql-tag"

export default gql`
  query GetDatastoreSchemaNames($datastoreId: ID!) {
    schemaNamesByDatastore(datastoreId: $datastoreId)
  }
`
