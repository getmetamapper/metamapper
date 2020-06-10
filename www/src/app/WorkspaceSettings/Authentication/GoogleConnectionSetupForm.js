import React from "react"
import { Button, Form, Input, Select, Col, Row } from "antd"
import { DEFAULT_PERMISSION, PERMISSION_CHOICES } from "lib/constants"
import FormLabel from "app/Common/FormLabel"
import Link from "app/Navigation/Link"
import RestrictedButton from "app/Common/RestrictedButton"

const GoogleConnectionSetupForm = ({
  form: { getFieldDecorator },
  domain,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="google-connection-form">
    <Row>
      <Col span={12}>
        <fieldset disabled={!hasPermission}>
          <Form.Item>
            <FormLabel required label="Domain" />
            <small>
              We will use the following GSuite-enabled domain to authenticate
              against:
            </small>
            {getFieldDecorator("entityId", {
              initialValue: domain,
              rules: [{ required: true, message: "This field is required." }],
            })(<Input type="text" value={domain} disabled />)}
          </Form.Item>
          <Form.Item>
            <FormLabel required label="Default Role" />
            <small>
              This is the default access role we will grant auto-provisioned
              users.
            </small>
            {getFieldDecorator("defaultPermissions", {
              initialValue: DEFAULT_PERMISSION,
              rules: [{ required: true, message: "This field is required." }],
            })(
              <Select>
                {Object.keys(PERMISSION_CHOICES).map((key, index) => (
                  <Select.Option key={key} value={key}>
                    {PERMISSION_CHOICES[key]}
                  </Select.Option>
                ))}
              </Select>
            )}
          </Form.Item>
          <Form.Item>
            <Link to="/settings/authentication">
              <Button type="default mr-10">Cancel</Button>
            </Link>
            <RestrictedButton
              type="primary"
              htmlType="submit"
              hasPermission={hasPermission}
              isSubmitting={isSubmitting}
            >
              {isSubmitting ? "Saving..." : "Save Changes"}
            </RestrictedButton>
          </Form.Item>
        </fieldset>
      </Col>
    </Row>
  </Form>
)

export default GoogleConnectionSetupForm
