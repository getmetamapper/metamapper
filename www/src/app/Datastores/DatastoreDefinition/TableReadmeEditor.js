import React, { Component } from "react"
import PropTypes from "prop-types"
const CodeMirror = window.CodeMirror

const IS_MOBILE = typeof navigator === 'undefined' || (
  navigator.userAgent.match(/Android/i)
    || navigator.userAgent.match(/webOS/i)
    || navigator.userAgent.match(/iPhone/i)
    || navigator.userAgent.match(/iPad/i)
    || navigator.userAgent.match(/iPod/i)
    || navigator.userAgent.match(/BlackBerry/i)
    || navigator.userAgent.match(/Windows Phone/i)
)

class CodeMirrorEditor extends React.Component {
  constructor(props) {
    super(props)
    this.state = {isControlled: Boolean(this.props.value)}
    this.handleChange = this.handleChange.bind(this)
    this.editorRef = React.createRef()
  }

  componentDidMount() {
    const isTextArea = this.props.forceTextArea || IS_MOBILE;
    if (!isTextArea) {
      this.editor = CodeMirror.fromTextArea(this.editorRef.current, this.props);
      this.editor.on('change', this.handleChange);
    }
  }

  componentDidUpdate() {
    if (!this.editor) {
      return
    }

    if (this.props.value) {
      if (this.editor.getValue() !== this.props.value) {
        this.editor.setValue(this.props.value);
      }
    }
  }

  handleChange() {
    if (!this.editor) {
      return
    }

    const value = this.editor.getValue()
    if (value === this.props.value) {
      return
    }

    if (this.props.onChange) {
      this.props.onChange({target: {value: value}})
    }

    if (this.editor.getValue() !== this.props.value) {
      if (this.state.isControlled) {
        this.editor.setValue(this.props.value)
      } else {
        this.props.value = value
      }
    }
  }

  render() {
    const editor = React.createElement('textarea', {
      ref: this.editorRef,
      value: this.props.value,
      readOnly: this.props.readOnly,
      defaultValue: this.props.defaultValue,
      onChange: this.props.onChange,
      className: this.props.textAreaClassName
    })

    return React.createElement('div', null, editor);
  }
}

const DefinitionReadmeEditor = (props) => {
  return (
    <form className="editor">
      <CodeMirrorEditor mode="markdown" theme="solarized" value={props.value} onChange={props.onChange} />
    </form>
  )
}

DefinitionReadmeEditor.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string
}

DefinitionReadmeEditor.defaultProps = {
  value: ''
}

export default DefinitionReadmeEditor

