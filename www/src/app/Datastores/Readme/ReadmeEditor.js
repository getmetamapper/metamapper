import React from "react"
import PropTypes from "prop-types"
import CodeMirrorEditor from "app/Common/CodeMirror/CodeMirrorEditor"

const ReadmeEditor = (props) => {
  return (
    <form className="editor">
      <CodeMirrorEditor
        mode="markdown"
        theme="monokai"
        value={props.value}
        onChange={props.onChange}
      />
    </form>
  )
}

ReadmeEditor.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string
}

ReadmeEditor.defaultProps = {
  value: ''
}

export default ReadmeEditor
