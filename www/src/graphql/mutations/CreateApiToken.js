import gql from "graphql-tag"

export default gql`
  mutation CreateApiToken(
    $name: String!
  ) {
    createApiToken(input: {
      name: $name,
    }) {
      apiToken {
        id
        name
      }
      secret
      errors {
        resource
        field
        code
      }
    }
  }
`
