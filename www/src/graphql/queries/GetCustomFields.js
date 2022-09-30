import gql from "graphql-tag"

export default gql`
  query GetCustomFields($contentType: String!) {
    customFields(contentType: $contentType) {
      edges {
        node {
          id
          pk
          fieldName
          fieldType
          shortDesc
          validators
        }
      }
    }
  }
`
