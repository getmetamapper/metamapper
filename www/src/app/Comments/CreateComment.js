import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import CreateCommentMutation from "graphql/mutations/CreateComment"
import GetComments from "graphql/queries/GetComments"
import RestrictedButton from "app/Common/RestrictedButton"
import TextEditor from "app/Common/TextEditor"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class CreateComment extends Component {
  constructor(props) {
    super(props)

    this.state = {
      html: null,
      text: null,
    }

    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  shouldComponentUpdate(nextProps, nextState) {
    return nextState.html === null || nextProps.submitting !== this.props.submitting
  }

  handleSubmit(evt) {
    evt.preventDefault()

    const {
      contentObject: { id: objectId },
      parentId,
    } = this.props
    const { html, text } = this.state

    if (!text) {
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
      html: null,
    })
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

  handleChange(content, delta, source, editor) {
    this.setState({
      html: editor.getHTML(),
      text: editor.getText(),
    })
  }

  // https://github.com/SmallImprovements/quill-auto-links
  render() {
    const { hasPermission, submitting } = this.props
    return (
      <div className="create-comment" data-test="CreateComment">
        <TextEditor
          data-test="CreateComment.Input"
          value={this.state.html}
          onChange={this.handleChange}
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
  withGraphQLMutation,
)(CreateComment)
