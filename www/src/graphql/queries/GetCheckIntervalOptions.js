import gql from "graphql-tag"

export default gql`
query GetCheckIntervalOptions {
  checkIntervalOptions {
    label
    value
  }
}
`
