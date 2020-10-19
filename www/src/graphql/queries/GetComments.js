import gql from "graphql-tag"

export default gql`
  query getComments($objectId: ID!) {
    comments(objectId: $objectId) {
      edges {
        node {
          id
          html
          numVoteUp
          numVoteDown
          author {
            pk
            name
            email
            avatarUrl
            isCurrentUser
          }
          createdAt
          isPinned
          pinnedAt
          pinnedBy {
            name
          }
          childComments {
            id
            html
            numVoteUp
            numVoteDown
            author {
              pk
              name
              email
              avatarUrl
              isCurrentUser
            }
            createdAt
          }
        }
      }
    }
  }
`
