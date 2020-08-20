import gql from "graphql-tag"

export default gql`
  mutation UpdateAssetOwner(
    $id: ID!
    $order: Int!
  ) {
    updateAssetOwner(input: {
      id: $id,
      order: $order,
    }) {
      assetOwner {
        type
        order
        owner {
          name
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
