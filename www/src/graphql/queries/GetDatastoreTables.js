import gql from "graphql-tag"

export default gql`
  query GetDatastoreTables($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      id
      pk
      slug
      name
      isEnabled
      jdbcConnection {
        engine
      }
      schemas(first: 5) {
        pk
        name
        tables {
          id
          name
          kind
          shortDesc
        }
      }
    }
  }
`
