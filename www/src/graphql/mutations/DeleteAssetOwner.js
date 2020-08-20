import gql from "graphql-tag"

export default gql`
  mutation DeleteAssetOwner($id: ID!) {
    deleteAssetOwner(input: {
      id: $id,
    }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
