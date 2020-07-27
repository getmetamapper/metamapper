import gql from "graphql-tag"

export default gql`
  mutation updateWorkspace(
    $id: ID!
    $name: String
    $slug: String
    $beaconConsent: Boolean
  ) {
    updateWorkspace(
      input: { id: $id, name: $name, slug: $slug, beaconConsent: $beaconConsent }
    ) {
      workspace {
        id
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
