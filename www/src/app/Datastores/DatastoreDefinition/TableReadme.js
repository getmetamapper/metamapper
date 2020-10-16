import React from "react"
import ReactMarkdown from "react-markdown"
import { withRouter } from "react-router-dom"
import { Button, Card, Icon, Tooltip } from "antd"
import Link from "app/Navigation/Link"

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
