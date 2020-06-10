import React from "react"
import { Row, Col, Card } from "antd"
import GoogleConnectionSetup from "app/WorkspaceSettings/Authentication/GoogleConnectionSetup"
import withGetSSOConnectionPrimaryKey from "graphql/withGetSSOConnectionPrimaryKey"

const AuthenticationSetupOAuth2Google = ({ ssoPrimaryKey, loading }) => (
  <Row>
    <Col span={12} offset={6}>
      <Card>
        <h2>Setup Single Sign-On with Google</h2>
        <p>We need the following information to set up this connection:</p>
        <GoogleConnectionSetup
          ssoConnection={{
            pk: ssoPrimaryKey,
            provider: "GOOGLE",
            mappings: {},
          }}
          loading={loading}
        />
      </Card>
    </Col>
  </Row>
)

export default withGetSSOConnectionPrimaryKey(AuthenticationSetupOAuth2Google)
