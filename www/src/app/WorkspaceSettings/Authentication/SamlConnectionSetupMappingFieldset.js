import React from "react"
import FormLabel from "app/Common/FormLabel"
import { Input, Form } from "antd"

const SamlConnectionSetupMappingFieldset = ({
  form: { getFieldDecorator },
  ssoConnection: { mappings },
}) => (
  <>
    <Form.Item>
      <FormLabel label="User ID" required />
      <small>This is the login URL provided by your identity provider.</small>
      {getFieldDecorator("extras.mappings.user_id", {
        initialValue: mappings.user_id,
        rules: [{ required: true, message: "This field is required." }],
      })(<Input type="text" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="User Email" required />
      <small>This is the login URL provided by your identity provider.</small>
      {getFieldDecorator("extras.mappings.user_email", {
        initialValue: mappings.user_email,
        rules: [{ required: true, message: "This field is required." }],
      })(<Input type="text" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="First Name" required />
      <small>This is the login URL provided by your identity provider.</small>
      {getFieldDecorator("extras.mappings.fname", {
        initialValue: mappings.fname,
        rules: [{ required: true, message: "This field is required." }],
      })(<Input type="text" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Last Name" required />
      <small>This is the login URL provided by your identity provider.</small>
      {getFieldDecorator("extras.mappings.lname", {
        initialValue: mappings.lname,
        rules: [{ required: true, message: "This field is required." }],
      })(<Input type="text" />)}
    </Form.Item>
  </>
)

export default SamlConnectionSetupMappingFieldset
