import React, { Component } from "react"
import { Col, Row } from "antd"
import TableReadmeEditor from "app/Datastores/DatastoreDefinition/TableReadmeEditor"
import TableReadmePreview from "app/Datastores/DatastoreDefinition/TableReadmePreview"

class DefinitionReadmeEditor extends Component {
  render() {
    return (
       <Row style={{ backgroundColor: 'white', height: '100%' }}>
        <Col span={12}>
          <TableReadmeEditor />
        </Col>
        <Col span={12} style={{ borderLeft: '3px solid #eee' }}>
          <TableReadmeEditor />
        </Col>
      </Row>
    )
  }
}

export default DefinitionReadmeEditor
