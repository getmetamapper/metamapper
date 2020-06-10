import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { TrixEditor } from "react-trix"
import GetComments from "graphql/queries/GetComments"
import UpdateCommentMutation from "graphql/mutations/UpdateComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import RestrictedButton from "app/Common/RestrictedButton"

class UpdateComment extends Component {
  constructor(props) {
    super(props)

    this.state = {
      bodyHtml: null,
      bodyText: null,
      editor: null,
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
    this.handleEditorReady = this.handleEditorReady.bind(this)
  }

  handleEditorReady(editor) {
    editor.insertHTML(this.props.html)
    this.setState({ editor })
  }

  handleSubmit(evt) {
    evt.preventDefault()

    const {
      contentObject: { id: objectId },
      commentId: id,
    } = this.props
    const { bodyHtml: html } = this.state

    if (!html) {
      return
    }

    const payload = {
      successMessage: "Comment has been added.",
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

  handleChange(bodyHtml, bodyText) {
    this.setState({
      bodyHtml,
      bodyText,
    })
  }

  render() {
    const { hasPermission, submitting } = this.props
    return (
      <div className="update-comment" data-test="UpdateComment">
        <TrixEditor
          data-test="UpdateComment.Input"
          onChange={this.handleChange}
          onEditorReady={this.handleEditorReady}
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
