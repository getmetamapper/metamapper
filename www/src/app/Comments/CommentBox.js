import React from "react"
import { TrixEditor } from "react-trix"

const CommentBox = (props) => (
  <div className="comment-box">
    <TrixEditor
      onChange={this.handleChange}
      onEditorReady={this.handleEditorReady}
    />
  </div>
)

export default CommentBox
