import gql from "graphql-tag"

export default gql`
  query GetDatastoreDefinitionBySlug($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      id
      pk
      slug
      name
      tags
      version
      isEnabled
      hasIndexes
      jdbcConnection {
        engine
      }
    }
  }
`
