import React, { Component } from "react"
import { Button } from "antd"
import CodeEditor from "app/Common/CodeEditor"
import Readme from "app/Datastores/Readme/Readme"

class ReadmeEditor extends Component {
  constructor(props) {
    super(props)

    this.handleMarkdownChange = this.handleMarkdownChange.bind(this)
    this.state = {
      markdownSrc: props.markdown,
      htmlMode: props.htmlMode,
    }
  }

  handleMarkdownChange(evt) {
    this.setState({
      markdownSrc: evt.target.value
    })

    if (this.props.onChange) {
      this.props.onChange(evt.target.value)
    }
  }

  render() {
    const {
      title,
      submitting,
      onSubmit,
      onClose,
    } = this.props
    return (
      <div className="markdown-editor" data-test="ReadmeEditor">
        <div className="editor-options fixed">
          <div className="title" data-test="ReadmeEditor.Title">
            {title}
          </div>
          <div className="buttons">
            <Button type="primary" onClick={onSubmit} disabled={submitting} data-test="ReadmeEditor.Submit">
              {submitting ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button onClick={onClose} data-test="ReadmeEditor.Close">Close</Button>
          </div>
        </div>
        <div className="editor-pane" data-test="ReadmeEditor.Editor">
          <CodeEditor
            value={this.state.markdownSrc}
            onChange={this.handleMarkdownChange}
          />
        </div>
        <div className="result-pane">
          <Readme
            className="result"
            markdown={this.state.markdownSrc}
            skipHtml={this.state.htmlMode === 'skip'}
            escapeHtml={this.state.htmlMode === 'escape'}
          />
        </div>
      </div>
    )
  }
}

ReadmeEditor.defaultProps = {
  htmlMode: 'raw',
}

export default ReadmeEditor
