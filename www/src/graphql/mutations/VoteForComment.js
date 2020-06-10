import gql from "graphql-tag"

export default gql`
  mutation VoteForComment($id: ID!, $action: String!) {
    voteForComment(input: { id: $id, action: $action }) {
      comment {
        pk
        numVoteUp
        numVoteDown
      }
      errors {
        resource
        field
        code
      }
    }
  }
`
