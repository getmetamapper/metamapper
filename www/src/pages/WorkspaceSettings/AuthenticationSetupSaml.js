import React from "react"
import { Row, Col } from "antd"
import SamlConnectionSetup from "app/WorkspaceSettings/Authentication/SamlConnectionSetup"
import withGetSSOConnectionPrimaryKey from "graphql/withGetSSOConnectionPrimaryKey"

const AuthenticationSetupSaml = ({ ssoPrimaryKey, loading }) => (
  <Row>
    <Col span={12} offset={6}>
      <SamlConnectionSetup
        ssoConnection={{
          pk: ssoPrimaryKey,
          provider: "GENERIC",
          mappings: {},
        }}
        loading={loading}
      />
    </Col>
  </Row>
)

export default withGetSSOConnectionPrimaryKey(AuthenticationSetupSaml)
