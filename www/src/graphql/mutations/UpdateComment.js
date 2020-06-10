import gql from "graphql-tag"

export default gql`
  mutation UpdateComment($id: ID!, $html: String!) {
    updateComment(input: { id: $id, html: $html }) {
      comment {
        pk
        html
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
