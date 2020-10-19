import React, { Fragment } from "react"
import Markdown from "react-markdown"
import CodeBlock from "app/Common/CodeMirror/CodeBlock"

const Readme = ({ markdown, emptyText, ...props }) => (
  <div className="readme">
    {markdown ? (
      <Markdown
        renderers={{ code: CodeBlock }}
        {...props}
      >
        {markdown}
      </Markdown>
    ) : (
      <Fragment>
        {emptyText}
      </Fragment>
    )}
  </div>
)

export default Readme
