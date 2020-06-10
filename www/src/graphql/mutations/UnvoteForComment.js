import gql from "graphql-tag"

export default gql`
  mutation UnvoteForComment($id: ID!) {
    unvoteForComment(input: { id: $id }) {
      ok
      errors {
        resource
        field
        code
      }
    }
  }
`
