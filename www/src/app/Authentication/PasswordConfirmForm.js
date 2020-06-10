import React from "react"
import { withRouter } from "react-router-dom"
import { Button, Input, Icon, Divider, Form } from "antd"
import PasswordInput from "app/Common/PasswordInput"
import { passwordStrengthValidator } from "lib/validators"

const PasswordConfirmForm = ({
  form: { getFieldDecorator, getFieldValue },
  match: { params },
  onSubmit,
  submitting,
}) => {
  const compareToFirstPassword = (rule, value, callback) => {
    if (value && value !== getFieldValue("password")) {
      callback("The two provided passwords are not the same.")
    } else {
      callback()
    }
  }

  return (
    <Form onSubmit={onSubmit} className="login-form">
      <Divider />
      <Form.Item label="Password" style={{ marginBottom: 8 }}>
        {getFieldDecorator("password", {
          rules: [{ validator: passwordStrengthValidator }],
        })(
          <PasswordInput
            prefix={<Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="password"
            placeholder="correctbatteryhorsestaple"
            strengthMeter
          />
        )}
      </Form.Item>
      <Form.Item label="Confirm Password">
        {getFieldDecorator("confirm_password", {
          rules: [{ validator: compareToFirstPassword }],
        })(
          <PasswordInput
            prefix={<Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="password"
            placeholder="correctbatteryhorsestaple"
            required
          />
        )}
      </Form.Item>
      <div>
        {getFieldDecorator("uid", { initialValue: params.uid })(
          <Input type="hidden" />
        )}
        {getFieldDecorator("token", { initialValue: params.token })(
          <Input type="hidden" />
        )}
      </div>
      <Form.Item>
        <Button block type="primary" htmlType="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Change Password"}
        </Button>
      </Form.Item>
    </Form>
  )
}

export default withRouter(PasswordConfirmForm)
