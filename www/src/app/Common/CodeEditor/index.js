import React from "react"
import PropTypes from "prop-types"
import CodeMirrorEditor from "app/Common/CodeMirror/CodeMirrorEditor"

const CodeEditor = ({ mode, value, onChange }) => (
  <form className="editor" data-test="CodeEditor">
    <CodeMirrorEditor
      mode={mode}
      theme="base16-light"
      value={value}
      onChange={onChange}
      placeholder="read"
      lineWrapping={true}
      lineNumbers={true}
    />
  </form>
)

CodeEditor.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string
}

CodeEditor.defaultProps = {
  value: '',
  mode: 'markdown',
}

export default CodeEditor
