import React from "react"
import { Form, Button } from "antd"
import PasswordInput from "app/Common/PasswordInput"
import { passwordStrengthValidator } from "lib/validators"

class UpdatePasswordForm extends React.Component {
  state = {}

  compareToFirstPassword = (rule, value, callback) => {
    const { form } = this.props
    if (value && value !== form.getFieldValue("password")) {
      callback("Confirmation must match new password.")
    } else {
      callback()
    }
  }

  render() {
    const {
      form: { getFieldDecorator },
      onSubmit,
      isSubmitting,
    } = this.props
    return (
      <Form className="update-password-form" onSubmit={onSubmit}>
        <Form.Item label="Current Password">
          {getFieldDecorator("currentPassword", {
            validateTrigger: false,
            rules: [{ required: true, message: "This field is required." }],
          })(<PasswordInput type="password" data-test="UpdatePasswordForm.CurrentPassword" />)}
        </Form.Item>
        <Form.Item label="New Password">
          {getFieldDecorator("password", {
            validateTrigger: false,
            rules: [
              { validator: passwordStrengthValidator },
              { required: true, message: "This field is required." },
            ],
          })(<PasswordInput type="password" data-test="UpdatePasswordForm.NewPassword" strengthMeter />)}
        </Form.Item>
        <Form.Item label="Confirm Password">
          {getFieldDecorator("confirmPassword", {
            validateTrigger: false,
            rules: [
              { validator: this.compareToFirstPassword },
              { required: true, message: "This field is required." },
            ],
          })(<PasswordInput type="password" data-test="UpdatePasswordForm.ConfirmPassword" />)}
        </Form.Item>
        <Form.Item>
          <Button
            block
            type="primary"
            className="btn-tall"
            htmlType="submit"
            disabled={isSubmitting}
            data-test="UpdatePasswordForm.Submit"
          >
            {isSubmitting ? "Saving..." : "Change Password"}
          </Button>
        </Form.Item>
      </Form>
    )
  }
}

export default UpdatePasswordForm
