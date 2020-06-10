import gql from "graphql-tag"

export default gql`
  query getWorkspaceBySlug($slug: String!) {
    workspaceBySlug(slug: $slug) {
      id
      pk
      name
      slug
      sshPublicKey
    }
  }
`
