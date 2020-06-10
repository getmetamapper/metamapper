import gql from "graphql-tag"

export default gql`
  mutation DomainHasSSOEnabled($domain: String!) {
    domainHasSSOEnabled(domain: $domain) {
      isSSOEnabled
      workspaceSlug
    }
  }
`
