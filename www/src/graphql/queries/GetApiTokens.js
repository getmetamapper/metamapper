import gql from "graphql-tag"

export default gql`
  query GetApiTokens {
    apiTokens {
      edges {
        node {
          id
          name
          isEnabled
          createdAt
        }
      }
    }
  }
`
