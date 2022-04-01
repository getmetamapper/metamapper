import gql from "graphql-tag"

export default gql`
  mutation EnableApiToken($id: ID!, $isEnabled: Boolean) {
    updateApiToken(input: {
      id: $id,
      isEnabled: $isEnabled
    }) {
      apiToken {
        id
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
