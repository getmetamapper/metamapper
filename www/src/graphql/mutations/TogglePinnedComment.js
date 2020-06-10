import gql from "graphql-tag"

export default gql`
  mutation TogglePinnedComment($id: ID!) {
    togglePinnedComment(input: { id: $id }) {
      comment {
        pk
        isPinned
        pinnedBy {
          email
        }
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
