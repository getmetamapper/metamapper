import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Popconfirm } from "antd"
import GetComments from "graphql/queries/GetComments"
import TogglePinnedCommentMutation from "graphql/mutations/TogglePinnedComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class PinComment extends Component {
  constructor(props) {
    super(props)

    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleSubmit(evt) {
    evt.preventDefault()

    const { commentId, objectId } = this.props
    const payload = {
      successMessage: null,
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

  handleSubmitSuccess = ({ data }) => {}

  render() {
    const { isPinned } = this.props
    return (
      <Popconfirm
        title={`Are you sure you want to ${
          isPinned ? "unpin" : "pin"
        } this comment?`}
        onConfirm={this.handleSubmit}
        okText="Yes"
        cancelText="No"
        data-test="PinComment.Popconfirm"
      >
        <span data-test="PinComment.Submit">
          {isPinned ? "unpin" : "pin"}
        </span>
      </Popconfirm>
    )
  }
}

PinComment.propTypes = {
  objectId: PropTypes.string.isRequired,
  commentId: PropTypes.string.isRequired,
}

export default compose(
  graphql(TogglePinnedCommentMutation),
  withGraphQLMutation
)(PinComment)
