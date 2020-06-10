import gql from "graphql-tag"

export default gql`
  mutation EnableSSOConnection($id: ID!, $isEnabled: Boolean) {
    updateSSOConnection(input: { id: $id, isEnabled: $isEnabled }) {
      ssoConnection {
        id
        pk
        name
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
