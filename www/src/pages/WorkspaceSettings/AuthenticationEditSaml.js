import React from "react"
import { compose } from "react-apollo"
import { Row, Col } from "antd"
import UpdateSamlConnection from "app/WorkspaceSettings/Authentication/UpdateSamlConnection"
import withGetSSOConnection from "graphql/withGetSSOConnection"

const AuthenticationEditSaml = ({ ssoConnection, loading }) => (
  <Row>
    <Col span={12} offset={6}>
      <UpdateSamlConnection ssoConnection={ssoConnection} loading={loading} />
    </Col>
  </Row>
)

export default compose(withGetSSOConnection)(AuthenticationEditSaml)
