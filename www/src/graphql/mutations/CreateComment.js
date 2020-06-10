import gql from "graphql-tag"

export default gql`
  mutation CreateComment($objectId: ID!, $html: String!, $parentId: ID) {
    createComment(
      input: { objectId: $objectId, html: $html, parentId: $parentId }
    ) {
      comment {
        html
        parent {
          pk
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
