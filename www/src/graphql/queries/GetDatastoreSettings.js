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
      objectPermissionsEnabled
      shortDesc
      hasIndexes
      disabledDatastoreProperties
      disabledTableProperties
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
