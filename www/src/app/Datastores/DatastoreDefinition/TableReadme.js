import React from "react"
import { withRouter } from "react-router-dom"
import { Button, Card } from "antd"
import Link from "app/Navigation/Link"
import Readme from "app/Datastores/Readme/Readme"

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
        <Readme
          markdown={tableDefinition.readme}
          emptyText={
            <div className="empty-text">
              You can <Link to={editReadmeUrl}>add a README</Link> with an overview of this table.
            </div>
          }
        />
      </Card>
    </div>
  )
}

export default withRouter(TableReadme)
