import gql from "graphql-tag"

export default gql`
  query GetSSODomains {
    ssoDomains {
      edges {
        node {
          id
          pk
          domain
          verificationStatus
          verificationToken
        }
      }
    }
  }
`
