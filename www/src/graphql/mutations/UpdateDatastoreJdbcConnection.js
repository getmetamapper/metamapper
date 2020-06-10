import gql from "graphql-tag"

export default gql`
  mutation UpdateDatastoreJdbcConnection(
    $id: ID!
    $username: String
    $password: String
    $database: String
    $host: String
    $port: Int
    $sshEnabled: Boolean
    $sshHost: String
    $sshUser: String
    $sshPort: Int
  ) {
    updateDatastoreJdbcConnection(
      input: {
        id: $id
        username: $username
        password: $password
        database: $database
        host: $host
        port: $port
        sshEnabled: $sshEnabled
        sshHost: $sshHost
        sshUser: $sshUser
        sshPort: $sshPort
      }
    ) {
      datastore {
        id
        jdbcConnection {
          engine
          host
          username
          database
          port
        }
        sshConfig {
          isEnabled
          host
          user
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
