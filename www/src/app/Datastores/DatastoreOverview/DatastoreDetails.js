import React from "react"
import { Card, Col, Row, Tag, Tooltip } from "antd"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"
import DatastoreDescription from "app/Datastores/DatastoreOverview/DatastoreDescription"
import DatastoreTags from "app/Datastores/DatastoreOverview/DatastoreTags"

const DatastoreDetails = ({ datastore }) => (
  <Card className="datastore-details">
    <Row>
      <Col span={18}>
        <h3>
          <DatastoreEngineIcon datastore={datastore} />
          <span className="ml-20">{datastore.name}</span>
        </h3>
      </Col>
      <Col span={6} className="text-right">
        {datastore.version && (
          <Tooltip title="Database Version">
            <Tag>{datastore.version}</Tag>
          </Tooltip>
        )}
      </Col>
    </Row>
    <div className="mb-16">
      <DatastoreDescription datastore={datastore} />
    </div>
    <div className="mb-0">
      <DatastoreTags datastore={datastore} />
    </div>
  </Card>
)

export default DatastoreDetails
