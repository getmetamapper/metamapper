import gql from "graphql-tag"

export default gql`
  mutation UpdateCustomProperties($objectId: ID!, $properties: [JSONObject]!) {
    updateCustomProperties(
      input: { objectId: $objectId, properties: $properties }
    ) {
      customProperties
      errors {
        resource
        field
        code
      }
    }
  }
`
