import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import GetComments from "graphql/queries/GetComments"
import RestrictedButton from "app/Common/RestrictedButton"
import TextEditor from "app/Common/TextEditor"
import UpdateCommentMutation from "graphql/mutations/UpdateComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateComment extends Component {
  constructor(props) {
    super(props)

    this.state = {
      html: props.html,
      text: null,
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  shouldComponentUpdate(nextProps, nextState) {
    return nextProps.submitting !== this.props.submitting
  }

  handleSubmit(evt) {
    evt.preventDefault()

    const {
      contentObject: { id: objectId },
      commentId: id,
    } = this.props
    const { html, text } = this.state

    if (!text) {
      return
    }

    const payload = {
      successMessage: "Comment has been updated.",
      variables: {
        id,
        html,
      },
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
    const { errors } = data.updateComment

    if (!errors) {
      this.props.onSuccess()
    }
  }

  handleChange(content, delta, source, editor) {
    this.setState({
      html: editor.getHTML(),
      text: editor.getText(),
    })
  }

  render() {
    const { hasPermission, submitting } = this.props
    return (
      <div className="update-comment" data-test="UpdateComment">
        <TextEditor
          data-test="UpdateComment.Input"
          value={this.state.html}
          onChange={this.handleChange}
        />
        <div className="update-comment-btn">
          <RestrictedButton
            block
            type="primary"
            htmlType="submit"
            hasPermission={hasPermission}
            isSubmitting={submitting}
            onClick={this.handleSubmit}
            data-test="UpdateComment.Submit"
          >
            {submitting ? "Saving..." : "Update Comment"}
          </RestrictedButton>
        </div>
      </div>
    )
  }
}

export default compose(
  graphql(UpdateCommentMutation),
  withGraphQLMutation
)(UpdateComment)
