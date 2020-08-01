import gql from "graphql-tag"

export default gql`
  query GetRecentUserActivities($userId: ID!) {
    recentUserActivities(userId: $userId, first: 20) {
      edges {
        node {
          verb
          oldValues
          newValues
          actor {
            id
            pk
            name
            email
          }
          target {
            id
            pk
            objectType
            displayName
            parentResource {
              pk
              displayName
              parentResource {
                pk
                displayName
              }
            }
          }
          actionObject {
            id
            pk
            objectType
          }
          timestamp
        }
      }
    }
  }
`
