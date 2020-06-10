import gql from "graphql-tag"

export default gql`
  mutation TestJdbcConnection(
    $engine: String!
    $username: String!
    $password: String!
    $database: String!
    $host: String!
    $port: Int!
    $sshEnabled: Boolean
    $sshHost: String
    $sshUser: String
    $sshPort: Int
  ) {
    testJdbcConnection(
      input: {
        engine: $engine
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
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
