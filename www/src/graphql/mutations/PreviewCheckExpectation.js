import gql from "graphql-tag"

export default gql`
mutation PreviewCheckExpectation(
  $handlerClass: String!
  $handlerInput: JSONObject!
  $passValueClass: String!
  $passValueInput: JSONObject!
) {
  previewCheckExpectation(input: {
    handlerClass: $handlerClass,
    handlerInput: $handlerInput,
    passValueClass: $passValueClass,
    passValueInput: $passValueInput,
  }) {
    expectation {
      handlerClass
      handlerInput
      passValueClass
      passValueInput
      description
    }
    errors {
      resource
      field
      code
    }
  }
}
`
