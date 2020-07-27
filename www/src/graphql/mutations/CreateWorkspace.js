import gql from "graphql-tag"

export default gql`
  mutation CreateWorkspace($name: String!, $slug: String!, $beaconConsent: Boolean) {
    createWorkspace(input: { name: $name, slug: $slug, beaconConsent: $beaconConsent }) {
      workspace {
        id
        pk
        name
        slug
        beaconConsent
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
