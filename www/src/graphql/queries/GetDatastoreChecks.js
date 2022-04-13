import gql from "graphql-tag"

export default gql`
query GetDatastoreChecks(
  $datastoreId: ID!
) {
  datastoreChecks: checks(datastoreId: $datastoreId) {
    edges {
      node {
        pk
        name
        isEnabled
        creator {
          name
        }
        lastExecution {
          status
          finishedAt
        }
      }
    }
  }
}
`
