import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { TrixEditor } from "react-trix"
import GetComments from "graphql/queries/GetComments"
import CreateCommentMutation from "graphql/mutations/CreateComment"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import RestrictedButton from "app/Common/RestrictedButton"

class CreateComment extends Component {
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
    editor.insertString("")
    this.setState({ editor })
  }

  handleSubmit(evt) {
    evt.preventDefault()

    const {
      contentObject: { id: objectId },
      parentId,
    } = this.props
    const { bodyHtml: html } = this.state

    if (!html) {
      return
    }

    const payload = {
      successMessage: "Comment has been added.",
      variables: {
        objectId,
        parentId,
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

  resetEditor = () => {
    this.setState({
      bodyHtml: "",
      bodyText: "",
    })

    this.state.editor.loadHTML("")
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.createComment

    if (!errors) {
      this.resetEditor()

      if (this.props.onSubmit) {
        this.props.onSubmit()
      }
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
      <div className="create-comment" data-test="CreateComment">
        <TrixEditor
          data-test="CreateComment.Input"
          onChange={this.handleChange}
          onEditorReady={this.handleEditorReady}
          disabled
        />
        <div className="create-comment-btn">
          <RestrictedButton
            block
            type="primary"
            htmlType="submit"
            hasPermission={hasPermission}
            isSubmitting={submitting}
            onClick={this.handleSubmit}
            data-test="CreateComment.Submit"
          >
            {submitting ? "Saving..." : "Comment"}
          </RestrictedButton>
        </div>
      </div>
    )
  }
}

CreateComment.defaultProps = {
  parentId: null,
  contentObject: {},
}

export default compose(
  graphql(CreateCommentMutation),
  withGraphQLMutation
)(CreateComment)
