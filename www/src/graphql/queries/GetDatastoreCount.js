import gql from "graphql-tag"

export default gql`
  query getDatastoreCount {
    datastores {
      totalCount
    }
  }
`
