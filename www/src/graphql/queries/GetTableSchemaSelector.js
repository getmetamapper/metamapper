import gql from "graphql-tag"

export default gql`
  query GetTableSchemaSelector($datastoreSlug: String!) {
    datastoreBySlug(slug: $datastoreSlug) {
      schemas {
        name
        tables {
          id
          name
        }
      }
    }
  }
`
