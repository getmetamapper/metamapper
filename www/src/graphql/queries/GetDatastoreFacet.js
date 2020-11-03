import gql from "graphql-tag"

export default gql`
query GetDatastoreFacet {
  datastores {
    edges {
      node {
        id
        pk
        slug
        name
        jdbcConnection {
          engine
        }
      }
    }
  }
  datastoreEngines
}
`
