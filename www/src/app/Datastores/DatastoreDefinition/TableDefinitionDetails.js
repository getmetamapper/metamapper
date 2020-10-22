import React from "react"
import { Card, Col, Row } from "antd"
import { withRouter } from "react-router-dom"
import TableDescription from "./TableDescription"
import TableLastCommitTimestamp from "./TableLastCommitTimestamp"
import TableDefinitionTags from "./TableDefinitionTags"
import withGetTableLastCommitTimestamp from "graphql/withGetTableLastCommitTimestamp"

const TableDefinitionDetails = ({
  table,
  schema,
  lastCommitTimestamp,
  loading,
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
      <TableDefinitionTags table={table} />
    </p>
  </Card>
)

export default withRouter(withGetTableLastCommitTimestamp(TableDefinitionDetails))
