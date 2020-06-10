import React from "react"
import { Button, Input, Icon, Form, Divider } from "antd"

const PasswordResetForm = ({
  form: { getFieldDecorator },
  onSubmit,
  submitting,
}) => (
  <Form className="password-reset-form" onSubmit={onSubmit}>
    <Divider />
    <Form.Item label="Email Address">
      {getFieldDecorator("email", {
        validateTrigger: false,
      })(
        <Input
          prefix={<Icon type="mail" style={{ color: "rgba(0,0,0,.25)" }} />}
          type="email"
          placeholder="hiro.protagonist@metaverse.io"
          data-test="PasswordResetForm.Email"
          required
        />
      )}
    </Form.Item>
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={submitting}
        data-test="PasswordResetForm.Submit"
      >
        {submitting ? "Submitting..." : "Send Password Reset Email"}
      </Button>
    </Form.Item>
  </Form>
)

export default PasswordResetForm
