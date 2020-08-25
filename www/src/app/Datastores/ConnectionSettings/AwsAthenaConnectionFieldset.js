import React, { useState, Fragment } from "react"
import { Card, Col, Form, Input, Row, Switch } from "antd"
import FormLabel from "app/Common/FormLabel"
import CopyInput from "app/Common/CopyInput"

const AwsAthenaConnectionFieldset = ({
  publicKey,
  datastore: { jdbcConnection, sshConfig },
  form: { getFieldDecorator, getFieldValue },
  hasPermission,
  onChange,
}) => {
  const [sshEnabled, setSshEnabled] = useState(sshConfig.isEnabled)
  return (
    <Fragment>
      <Form.Item>
        <FormLabel label="Role Address" required />
        {getFieldDecorator("extras.role", {
          initialValue: jdbcConnection.extras,
          rules: [],
        })(
          <Input
            type="text"
            onChange={onChange}
            disabled={!hasPermission}
            data-test="ConnectionSettingsFieldset.AwsRole"
          />
        )}
      </Form.Item>
      <Form.Item>
        <FormLabel label="Region" required />
        {getFieldDecorator("extras.region", {
          initialValue: jdbcConnection.extras,
          rules: [],
        })(
          <Input
            type="text"
            onChange={onChange}
            disabled={!hasPermission}
            data-test="ConnectionSettingsFieldset.AwsRegion"
          />
        )}
      </Form.Item>
      <Form.Item>
        <FormLabel label="Database" required />
        {getFieldDecorator("database", {
          initialValue: jdbcConnection.database,
          rules: [],
        })(
          <Input
            type="text"
            onChange={onChange}
            disabled={!hasPermission}
            data-test="ConnectionSettingsFieldset.Database"
          />
        )}
      </Form.Item>
      <Form.Item className="hidden">
        {getFieldDecorator("host", {
          initialValue: jdbcConnection.host || "athena.amazonaws.com",
          rules: [],
        })(<Input type="text" onChange={onChange} disabled={!hasPermission} />)}
      </Form.Item>
      <Form.Item className="hidden">
        {getFieldDecorator("username", {
          initialValue: jdbcConnection.username || "amazonapis",
          rules: [],
        })(<Input type="text" onChange={onChange} disabled={!hasPermission} />)}
      </Form.Item>
      <Form.Item className="hidden">
        {getFieldDecorator("password", {
          initialValue: jdbcConnection.password || "secret",
          rules: [],
        })(<Input type="text" onChange={onChange} disabled={!hasPermission} />)}
      </Form.Item>
      <Form.Item className="hidden">
        {getFieldDecorator("port", {
          initialValue: jdbcConnection.port || "443",
          rules: [],
        })(<Input type="text" onChange={onChange} disabled={!hasPermission} />)}
      </Form.Item>
      <Form.Item>
        <Card className="ssh-tunnel-enabled">
          <Row>
            <Col span={18}>
              <span className="label">Connect via SSH tunnel</span>
              <small>
                This method is necessary if your database is located in a
                private network.
              </small>
              <p className="mb-0">
                <small>
                  <a href="https://docs.metamapper.io">Read more here.</a>
                </small>
              </p>
            </Col>
            <Col span={6}>
              <span className="pull-right">
                {getFieldDecorator("sshEnabled", {
                  initialValue: sshEnabled,
                  rules: [],
                })(
                  <Switch
                    defaultChecked={sshEnabled}
                    onChange={() => setSshEnabled(!sshEnabled)}
                    disabled={!hasPermission}
                    data-test="ConnectionSettingsFieldset.SSHEnabled"
                  />
                )}
              </span>
            </Col>
          </Row>
        </Card>
        {sshEnabled && (
          <div className="ssh-tunnel-form">
            <Form.Item>
              <FormLabel label="SSH Host" required />
              {getFieldDecorator("sshHost", {
                initialValue: sshConfig.host,
                rules: [],
              })(
                <Input
                  type="text"
                  onChange={onChange}
                  disabled={!hasPermission}
                  data-test="ConnectionSettingsFieldset.SSHHost"
                />
              )}
            </Form.Item>
            <Form.Item>
              <FormLabel label="SSH Port" required />
              {getFieldDecorator("sshPort", {
                initialValue: sshConfig.port,
                rules: [],
              })(
                <Input
                  type="text"
                  onChange={onChange}
                  disabled={!hasPermission}
                  data-test="ConnectionSettingsFieldset.SSHPort"
                />
              )}
            </Form.Item>
            <Form.Item>
              <FormLabel label="SSH User" required />
              {getFieldDecorator("sshUser", {
                initialValue: sshConfig.user,
                rules: [],
              })(
                <Input
                  type="text"
                  onChange={onChange}
                  disabled={!hasPermission}
                  data-test="ConnectionSettingsFieldset.SSHUser"
                />
              )}
            </Form.Item>
            <Form.Item>
              <FormLabel label="Public Key" />
              <CopyInput value={publicKey} disabled />
            </Form.Item>
          </div>
        )}
      </Form.Item>
    </Fragment>
  )
}

AwsAthenaConnectionFieldset.defaultProps = {
  datastore: {
    jdbcConnection: {},
    sshConfig: {
      isEnabled: false,
    },
  },
}

export default AwsAthenaConnectionFieldset
