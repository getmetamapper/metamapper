import React from "react"
import { compose } from "react-apollo"
import { Card, Col, Row } from "antd"
import { withRouter } from "react-router-dom"
import withGetTableLastCommitTimestamp from "graphql/withGetTableLastCommitTimestamp"
import TableDescription from "./TableDescription"
import TableLastCommitTimestamp from "./TableLastCommitTimestamp"
import TableDefinitionTags from "./TableDefinitionTags"
import TablePopularityBadge from "./TablePopularityBadge"

const TableDefinitionDetails = ({
  datastore,
  lastCommitTimestamp,
  loading,
  schema,
  table,
}) => (
  <Card className="table-definition-details">
    <Row>
      <Col span={18}>
        <h3>
          <small>{schema.name}.</small><span>{table.name}</span>
        </h3>
      </Col>
      <Col span={6} className="text-right">
        <TableLastCommitTimestamp
          loading={loading}
          timestamp={lastCommitTimestamp}
        />
      </Col>
    </Row>
    <p className="mb-0">
      <TableDescription table={table} />
    </p>
    <p className="mb-0">
      {datastore.supportedFeatures.usage && (
        <TablePopularityBadge
          popularityScore={table.usage.popularityScore}
          totalQueries={table.usage.totalQueries}
          totalUsers={table.usage.totalUsers}
          windowInDays={table.usage.windowInDays}
        />
      )}
      <TableDefinitionTags table={table} />
    </p>
  </Card>
)

export default compose(withRouter, withGetTableLastCommitTimestamp)(TableDefinitionDetails)
