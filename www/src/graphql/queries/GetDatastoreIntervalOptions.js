import gql from "graphql-tag"

export default gql`
query GetDatastoreIntervalOptions {
  datastoreIntervalOptions {
    label
    value
  }
}
`
