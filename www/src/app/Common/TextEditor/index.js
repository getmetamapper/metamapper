import React, { Component } from "react"
import ReactQuill from "react-quill"
import UserAvatar from "app/Common/UserAvatar"
import ReactDOMServer from "react-dom/server"
import { withUserContext } from "context/UserContext"
import "quill-mention"

class TextEditor extends Component {
  constructor(props) {
    super(props);

    this.toolbar = [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'color': [] }, { 'background': [] }],
      [{'list': 'ordered'}, {'list': 'bullet'}],
      ['link'],
      ['clean'],
    ]
  }

  handleSource = (searchTerm, renderList, mentionChar) => {
    const values = []

    if (searchTerm.length === 0) {
      renderList(values, searchTerm);
    } else {
      const matches = [];
      for (let i = 0; i < values.length; i++)
        if (
          ~values[i].value.toLowerCase().indexOf(searchTerm.toLowerCase())
        )
          matches.push(values[i]);
      renderList(matches, searchTerm);
    }
  }

  handleRenderItem = (item, searchTerm) => {
    return ReactDOMServer.renderToString(<><UserAvatar {...item} /> {item.value}</>)
  }

  render() {
    const { onChange, value } = this.props
    return (
      <span data-test={this.props['data-test']}>
        <ReactQuill
          ref={el => this.editor = el}
          theme="snow"
          onChange={onChange}
          value={value}
          modules={{
            syntax: {
              highlight: text => window.hljs.highlightAuto(text).value,
            },
            toolbar: this.toolbar,
            mention: {
              allowedChars: /^[A-Za-z\sÅÄÖåäö]*$/,
              minChars: 1,
              mentionDenotationChars: ["@", "#"],
              source: this.handleSource,
              renderItem: this.handleRenderItem,
            },
          }}
        />
      </span>
    )
  }
}

export default withUserContext(TextEditor)
