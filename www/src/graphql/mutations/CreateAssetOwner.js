import gql from "graphql-tag"

export default gql`
  mutation CreateAssetOwner(
    $objectId: ID!
    $ownerId: ID!
    $order: Int
  ) {
    createAssetOwner(input: {
      objectId: $objectId,
      ownerId: $ownerId,
      order: $order,
    }) {
      assetOwner {
        type
        owner {
          id
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
