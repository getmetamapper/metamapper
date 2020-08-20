import gql from "graphql-tag"

export default gql`
  query GetDatastores($search: String) {
    datastores(search: $search) {
      edges {
        node {
          id
          pk
          slug
          name
          isEnabled
          jdbcConnection {
            engine
          }
          latestRun {
            createdOn
          }
        }
      }
    }
  }
`
