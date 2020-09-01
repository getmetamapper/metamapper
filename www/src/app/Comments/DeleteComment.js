import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Popconfirm } from "antd"
import GetComments from "graphql/queries/GetComments"
import DeleteCommentMutation from "graphql/mutations/DeleteComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteComment extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { objectId, commentId } = this.props
    const payload = {
      successMessage: "Comment has been removed.",
      variables: { id: commentId },
      refetchQueries: [
        {
          query: GetComments,
          variables: {
            objectId,
          },
        },
      ],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    if (this.props.onSubmit) {
      this.props.onSubmit()
    }
  }

  render() {
    return (
      <Popconfirm
        title="Are you sure you want to delete this comment?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteComment.Confirm"
      >
        <span key="comment-delete" data-test="DeleteComment.Submit">
          delete
        </span>
      </Popconfirm>
    )
  }
}

DeleteComment.propTypes = {
  commentId: PropTypes.string.isRequired,
}

export default compose(
  graphql(DeleteCommentMutation),
  withGraphQLMutation
)(DeleteComment)
