import gql from "graphql-tag"

export default gql`
  mutation UpdateCustomField(
    $id: ID!
    $fieldName: String
    $shortDesc: String
    $validators: JSONObject
  ) {
    updateCustomField(
      input: {
        id: $id
        fieldName: $fieldName
        shortDesc: $shortDesc
        validators: $validators
      }
    ) {
      customField {
        fieldName
        fieldType
        validators
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
