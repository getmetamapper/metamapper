import React from "react"
import { Card, Col, Row } from "antd"
import TableDescription from "./TableDescription"
import TablePropertiesPillGroup from "./TablePropertiesPillGroup"
import TableDefinitionTags from "./TableDefinitionTags"

const TableDefinitionDetails = ({ table, schema, latestRun }) => (
  <Card className="table-definition-details">
    <Row>
      <Col span={18}>
        <h3>
          <small>{schema.name}.</small>
          {table.name}
        </h3>
      </Col>
      <Col span={6} className="text-right">
        <TablePropertiesPillGroup properties={table.properties} />
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

export default TableDefinitionDetails
