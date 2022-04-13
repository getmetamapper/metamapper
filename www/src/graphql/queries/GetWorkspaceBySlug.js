import gql from "graphql-tag"

export default gql`
  query GetWorkspaceBySlug($slug: String!) {
    workspaceBySlug(slug: $slug) {
      id
      pk
      name
      slug
      beaconConsent
      sshPublicKey
    }
  }
`
