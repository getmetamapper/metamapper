import React from "react"
import ReactMarkdown from "react-markdown"
import { withRouter } from "react-router-dom"
import { Button, Card, Icon, Tooltip } from "antd"
import Link from "app/Navigation/Link"


const initialSource = `
# Live demo
Changes are automatically rendered as you type.
## Table of Contents
* Implements [GitHub Flavored Markdown](https://github.github.com/gfm/)
* Renders actual, "native" React DOM elements
* Allows you to escape or skip HTML (try toggling the checkboxes above)
* If you escape or skip the HTML, no \`dangerouslySetInnerHTML\` is used! Yay!
## HTML block below
<blockquote>
  This blockquote will change based on the HTML settings above.
</blockquote>
## How about some code?
\`\`\`js
var React = require('react');
var Markdown = require('react-markdown');
React.render(
  <Markdown source="# Your markdown here" />,
  document.getElementById('content')
);
\`\`\`
Pretty neat, eh?
## Tables?
| Feature   | Support |
| --------- | ------- |
| tables    | ✔ |
| alignment | ✔ |
| wewt      | ✔ |
## More info?
Read usage information and more on [GitHub](//github.com/rexxars/react-markdown)
---------------
A component by [Espen Hovlandsdal](https://espen.codes/)
`

const TableReadme = ({
  match: {
    params: {
      datastoreSlug,
      schemaName,
      tableName,
    },
  },
  tableDefinition,
}) => {
  const editReadmeUrl = `/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}/readme/edit`
  return (
    <div className="table-readme">
      <Card
        title="README"
        extra={
          <Link to={editReadmeUrl}>
            <Button size="small" icon="edit" />
          </Link>
        }
      >
        {tableDefinition.readme ? (
          <ReactMarkdown source={tableDefinition.readme} />
        ) : (
          <div className="empty-text">
            You can <Link to={editReadmeUrl}>add a README</Link> with an overview of this table.
          </div>
        )}
      </Card>
    </div>
  )
}

export default withRouter(TableReadme)
