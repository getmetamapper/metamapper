import gql from "graphql-tag"

export default gql`
  query getCustomFields($contentType: String!) {
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
