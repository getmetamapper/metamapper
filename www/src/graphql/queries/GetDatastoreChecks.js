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
        tags
        creator {
          name
          email
          avatarUrl
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
