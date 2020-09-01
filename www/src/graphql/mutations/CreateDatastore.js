import gql from "graphql-tag"

export default gql`
  mutation CreateDatastore(
    $name: String!
    $tags: [String]
    $engine: String!
    $username: String!
    $password: String!
    $database: String!
    $host: String!
    $port: Int!
    $extras: JSONObject
    $sshEnabled: Boolean
    $sshHost: String
    $sshUser: String
    $sshPort: Int
  ) {
    createDatastore(
      input: {
        name: $name
        tags: $tags
        engine: $engine
        username: $username
        password: $password
        database: $database
        host: $host
        port: $port
        extras: $extras
        sshEnabled: $sshEnabled
        sshHost: $sshHost
        sshUser: $sshUser
        sshPort: $sshPort
      }
    ) {
      datastore {
        pk
        name
        slug
        isEnabled
        jdbcConnection {
          engine
        }
        sshConfig {
          isEnabled
          host
          port
        }
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
