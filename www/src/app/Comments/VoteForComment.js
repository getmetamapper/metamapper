import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Icon, Tooltip } from "antd"
import VoteForCommentMutation from "graphql/mutations/VoteForComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class VoteForComment extends Component {
  constructor(props) {
    super(props)

    const actions = {
      UP: 1,
      DOWN: -1,
    }

    this.state = {
      commentId: props.commentId,
      action: actions[props.action],
    }

    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleSubmit = () => {
    const { commentId, action } = this.state
    const payload = {
      successMessage: null,
      variables: {
        id: commentId,
        action,
      },
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    const { comment, errors } = data.voteForComment

    if (!errors) {
      this.props.onChange(comment)
    }
  }

  render() {
    const { action } = this.state
    const { count, icon, tooltip } = this.props
    return (
      <span key="comment-basic-like" data-test={`VoteForComment.${this.props.action}`}>
        <Tooltip title={tooltip}>
          <Icon
            type={icon}
            theme={action === "liked" ? "filled" : "outlined"}
            onClick={this.handleSubmit}
            data-test={`VoteForComment.${this.props.action}.Submit`}
          />
        </Tooltip>
        <span style={{ paddingLeft: 8, cursor: "auto" }}>{count}</span>
      </span>
    )
  }
}

const WrappedVoteForComment = compose(
  graphql(VoteForCommentMutation),
  withGraphQLMutation
)(VoteForComment)

export const UpvoteComment = ({ commentId, count, onChange }) => (
  <WrappedVoteForComment
    action="UP"
    commentId={commentId}
    count={count}
    icon="caret-up"
    tooltip="Like"
    onChange={onChange}
  />
)

export const DownvoteComment = ({ commentId, count, onChange }) => (
  <WrappedVoteForComment
    action="DOWN"
    commentId={commentId}
    count={count}
    icon="caret-down"
    tooltip="Dislike"
    onChange={onChange}
  />
)

export default WrappedVoteForComment
