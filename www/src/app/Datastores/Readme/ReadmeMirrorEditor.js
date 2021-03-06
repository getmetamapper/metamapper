import React, { Component } from "react"
import { Button } from "antd"
import ReadmeEditor from "app/Datastores/Readme/ReadmeEditor"
import Readme from "app/Datastores/Readme/Readme"

class ReadmeMirrorEditor extends Component {
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
      <div className="markdown-editor" data-test="ReadmeMirrorEditor">
        <div className="editor-options fixed">
          <div className="title" data-test="ReadmeMirrorEditor.Title">
            {title}
          </div>
          <div className="buttons">
            <Button type="primary" onClick={onSubmit} disabled={submitting} data-test="ReadmeMirrorEditor.Submit">
              {submitting ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button onClick={onClose} data-test="ReadmeMirrorEditor.Close">Close</Button>
          </div>
        </div>
        <div className="editor-pane" data-test="ReadmeMirrorEditor.Editor">
          <ReadmeEditor
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

ReadmeMirrorEditor.defaultProps = {
  htmlMode: 'raw'
}

export default ReadmeMirrorEditor
