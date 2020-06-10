import gql from "graphql-tag"

export default gql`
  mutation CreateCustomField(
    $fieldName: String!
    $fieldType: String!
    $validators: JSONObject!
    $shortDesc: String
    $contentType: String!
  ) {
    createCustomField(
      input: {
        fieldName: $fieldName
        fieldType: $fieldType
        validators: $validators
        shortDesc: $shortDesc
        contentType: $contentType
      }
    ) {
      customField {
        pk
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
