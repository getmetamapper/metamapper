import gql from "graphql-tag"

export default gql`
mutation CreateCheckExpectation(
  $id: ID!
  $handlerClass: String!
  $handlerInput: JSONObject!
  $passValueClass: String!
  $passValueInput: JSONObject!
) {
  createCheckExpectation(input: {
    id: $id
    handlerClass: $handlerClass,
    handlerInput: $handlerInput,
    passValueClass: $passValueClass,
    passValueInput: $passValueInput,
  }) {
    expectation {
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
