import React from "react"
import { Row, Col, Card } from "antd"
import GithubConnectionSetup from "app/WorkspaceSettings/Authentication/GithubConnectionSetup"
import withGetSSOConnectionPrimaryKey from "graphql/withGetSSOConnectionPrimaryKey"

const AuthenticationSetupOAuth2Github = ({ ssoPrimaryKey, loading }) => (
  <Row>
    <Col span={12} offset={6}>
      <Card>
        <h2>Setup Single Sign-On with Github</h2>
        <p>We need the following information to set up this connection:</p>
        <GithubConnectionSetup
          ssoConnection={{
            pk: ssoPrimaryKey,
            provider: "GITHUB",
            mappings: {},
          }}
          loading={loading}
        />
      </Card>
    </Col>
  </Row>
)

export default withGetSSOConnectionPrimaryKey(AuthenticationSetupOAuth2Github)
