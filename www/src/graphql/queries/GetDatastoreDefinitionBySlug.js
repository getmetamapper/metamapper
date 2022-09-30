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
      jdbcConnection {
        engine
      }
      supportedFeatures {
        checks
        indexes
        partitions
        usage
      }
      firstRunIsPending
    }
  }
`
