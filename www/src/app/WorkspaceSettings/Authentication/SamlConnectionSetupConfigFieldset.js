import React from "react"
import { Form, Input, Select } from "antd"
import { DEFAULT_PERMISSION, PERMISSION_CHOICES } from "lib/constants"
import FormLabel from "app/Common/FormLabel"

const SamlConnectionSetupConfigFieldset = ({
  form: { getFieldDecorator },
  ssoConnection: { pk, entityId, ssoUrl, x509cert },
}) => (
  <>
    <Form.Item>
      <FormLabel label="Issuer" required />
      <small>This field will be provided by your identity provider.</small>
      {getFieldDecorator("entityId", {
        initialValue: entityId,
      })(<Input type="text" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="SAML 2.0 Endpoint" required />
      <small>This is the login URL provided by your identity provider.</small>
      {getFieldDecorator("ssoUrl", {
        initialValue: ssoUrl,
      })(<Input type="text" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel required label="Default Role" />
      <small>
        This is the default access role we will grant auto-provisioned users.
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
      <FormLabel label="Public Certificate" required />
      <small>Copy and paste your x.509 certificate here.</small>
      {getFieldDecorator("x509cert", {
        initialValue: x509cert,
      })(<Input.TextArea rows={4} />)}
    </Form.Item>
  </>
)

export default SamlConnectionSetupConfigFieldset
