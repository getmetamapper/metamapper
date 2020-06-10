import gql from "graphql-tag"

export default gql`
  mutation DeleteComment($id: ID!) {
    deleteComment(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
