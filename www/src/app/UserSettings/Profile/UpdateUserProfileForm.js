import React from "react"
import { Form, Input, Button } from "antd"
import { emailValidator } from "lib/validators"
import FormLabel from "app/Common/FormLabel"
import PasswordInput from "app/Common/PasswordInput"

const UpdateUserProfileForm = ({
  form: { getFieldDecorator },
  user,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="update-user-form">
    <Form.Item>
      <FormLabel label="First Name" required />
      {getFieldDecorator("fname", {
        initialValue: user.fname,
        validateTrigger: false,
        rules: [
          { required: true, message: "This field is required." },
          { max: 60, message: "This field must be less than 60 characters." },
        ],
      })(<Input type="text" data-test="UpdateUserProfileForm.FirstName" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Last Name" required />
      {getFieldDecorator("lname", {
        initialValue: user.lname,
        validateTrigger: false,
        rules: [
          { required: true, message: "This field is required." },
          { max: 60, message: "This field must be less than 60 characters." },
        ],
      })(<Input type="text" data-test="UpdateUserProfileForm.LastName" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Email Address" required />
      {getFieldDecorator("email", {
        initialValue: user.email,
        validateTrigger: false,
        rules: [
          { required: true, message: "This field is required." },
          { validator: emailValidator },
        ],
      })(<Input type="text" data-test="UpdateUserProfileForm.Email" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Current Password" required />
      {getFieldDecorator("currentPassword", {
        validateTrigger: false,
        rules: [{ required: true, message: "This field is required." }],
      })(
        <PasswordInput
          data-test="UpdateUserProfileForm.CurrentPassword"
          placeholder="We require your current password to make these changes."
        />
      )}
    </Form.Item>
    <Form.Item>
      <Button
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="UpdateUserProfileForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Update Profile"}
      </Button>
    </Form.Item>
  </Form>
)

export default UpdateUserProfileForm
