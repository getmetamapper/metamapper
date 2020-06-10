import gql from "graphql-tag"

export default gql`
  mutation CreateSSODomain($domain: String!) {
    createSSODomain(input: { domain: $domain }) {
      ssoDomain {
        pk
        domain
        isVerified
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
