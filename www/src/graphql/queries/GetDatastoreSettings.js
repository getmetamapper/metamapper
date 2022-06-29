import gql from "graphql-tag"

export default gql`
  query GetDatastoreSettings($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      id
      pk
      slug
      name
      tags
      version
      isEnabled
      interval {
        label
        value
      }
      objectPermissionsEnabled
      shortDesc
      disabledDatastoreProperties
      disabledTableProperties
      incidentContacts
      supportedFeatures {
        checks
        indexes
        partitions
        usage
      }
      jdbcConnection {
        engine
        host
        username
        database
        port
        extras
      }
      sshConfig {
        isEnabled
        host
        user
        port
        publicKey
      }
      latestRun {
        createdOn
        finishedAt
      }
    }
  }
`
