import gql from "graphql-tag"

export default gql`
query GetCheckHandlerOptions {
  expectationHandlers: checkExpectationHandlers {
    name
    info
    handler
    details {
      name
      type
      label
      options
      helpText
    }
  }
  passValueHandlers: checkPassValueHandlers {
    name
    info
    handler
    details {
      name
      type
      label
      options
      helpText
    }
  }
}
`
