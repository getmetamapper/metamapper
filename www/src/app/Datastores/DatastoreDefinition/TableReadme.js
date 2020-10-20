import React, { Fragment } from "react"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
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
  hasPermission,
  tableDefinition,
}) => {
  const editReadmeUrl = `/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}/readme/edit`
  return (
    <div className="table-readme" data-test="TableReadme">
      <Card
        title="README"
        extra={
          <>
            {hasPermission && (
              <Link to={editReadmeUrl} data-test="TableReadme.Edit">
                <Button size="small" icon="edit" />
              </Link>
            )}
          </>
        }
      >
        <Readme
          markdown={tableDefinition.readme}
          emptyText={
            <div className="empty-text">
              {hasPermission ? (
                <Fragment>You can <Link to={editReadmeUrl}>add a README</Link> with an overview of this table.</Fragment>
              ) : (
                <Fragment>This table has no README.</Fragment>
              )}
            </div>
          }
        />
      </Card>
    </div>
  )
}

export default withRouter(withWriteAccess(TableReadme))
