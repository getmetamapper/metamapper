import React from "react"
import { Button, Row, Col, Tag } from "antd"
import moment from "moment"
import Link from "app/Navigation/Link"
import BooleanStatus from "app/Common/BooleanStatus"
import UpdateCheck from "app/Datastores/DatastoreChecks/UpdateCheck"

const CheckHeader = ({ check, datastore }) => (
  <div className="check-header">
    <Row>
      <Col span={16}>
        <h1>
          {check.name}
        </h1>
        <p>
          <BooleanStatus isEnabled={check.isEnabled} />
          <span class="dot"></span>
          <span>
            Created by <Link to={`/settings/users/${check.creator.id}`}>{check.creator.name}</Link> {moment(check.createdAt).fromNow()}
          </span>
        </p>
        <p>
          {check.tags.map(tag => <Tag color="blue">{tag}</Tag>)}
        </p>
      </Col>
      <Col span={8}>
        <div style={{ textAlign: "right" }}>
          <Link to={`/datastores/${datastore.slug}/checks/${check.pk}/sql/edit`}>
            <Button type="primary" icon="code" style={{ marginRight: 16 }}>
              SQL
            </Button>
          </Link>
          <UpdateCheck check={check} />
        </div>
      </Col>
    </Row>
  </div>
)

export default CheckHeader
