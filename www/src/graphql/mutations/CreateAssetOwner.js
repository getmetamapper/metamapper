import gql from "graphql-tag"

export default gql`
mutation CreateAssetOwner(
  $objectId: ID!
  $ownerId: ID!
  $classification: String!
  $order: Int
) {
  createAssetOwner(input: {
    objectId: $objectId,
    ownerId: $ownerId,
    classification: $classification,
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
