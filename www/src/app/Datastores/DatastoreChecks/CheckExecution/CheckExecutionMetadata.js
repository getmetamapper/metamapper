import React from "react"
import { Card, Col, Row } from "antd"
import moment from "moment"
import prettyMs from "pretty-ms"
import { TIMESTAMP_FORMAT } from "lib/constants"
import StatusBadge from "app/Common/StatusBadge"
import InfoItem from "app/Common/InfoItem"

const ExecutionMetadata = ({ status, startedAt, finishedAt }) => (
  <Card>
    <Row>
      <Col span={12}>
        <InfoItem
          label="Status"
          value={<StatusBadge status={status} />}
        />
      </Col>
      <Col span={12}>
        <InfoItem
          label="Duration"
          value={finishedAt && prettyMs(moment(finishedAt).diff(startedAt))}
        />
      </Col>
    </Row>
    <Row>
      <Col span={12}>
        <InfoItem
          label="Start Time"
          value={moment(startedAt).format(TIMESTAMP_FORMAT)}
        />
      </Col>
      <Col span={12}>
        <InfoItem
          label="Finish Time"
          value={finishedAt && moment(finishedAt).format(TIMESTAMP_FORMAT)}
        />
      </Col>
    </Row>
  </Card>
)

export default ExecutionMetadata
