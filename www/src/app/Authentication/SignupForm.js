import React from "react"
import qs from "query-string"
import { Form, Icon, Input, Button, Row, Divider, Col } from "antd"
import PasswordInput from "app/Common/PasswordInput"
import { passwordStrengthValidator } from "lib/validators"

const SignupForm = ({ form, onSubmit, submitting }) => {
  const { email } = qs.parse(window.location.search)
  return (
    <Form onSubmit={onSubmit} className="signup-form">
      <Divider />
      <Row>
        <Col span={24}>
          <Form.Item label="Email Address">
            {form.getFieldDecorator("email", {
              initialValue: email || "",
              validateTrigger: false,
              rules: [
                {
                  required: true,
                  message: "This field is required.",
                },
              ],
            })(
              <Input
                prefix={
                  <Icon type="mail" style={{ color: "rgba(0,0,0,.25)" }} />
                }
                type="email"
                placeholder="hiro.protagonist@metaverse.io"
                data-test="SignupForm.Email"
              />
            )}
          </Form.Item>
        </Col>
      </Row>
      <Row>
        <Col span={11} className="name-input">
          <Form.Item label="First Name">
            {form.getFieldDecorator("fname", {
              validateTrigger: false,
              rules: [
                {
                  required: true,
                  message: "This field is required.",
                },
              ],
            })(
              <Input
                prefix={
                  <Icon type="user" style={{ color: "rgba(0,0,0,.25)" }} />
                }
                type="text"
                placeholder="Hiro"
                data-test="SignupForm.FirstName"
              />
            )}
          </Form.Item>
        </Col>
        <Col span={12} offset={1} className="name-input">
          <Form.Item label="Last Name">
            {form.getFieldDecorator("lname", {
              validateTrigger: false,
              rules: [
                {
                  required: true,
                  message: "This field is required.",
                },
              ],
            })(
              <Input
                prefix={
                  <Icon type="team" style={{ color: "rgba(0,0,0,.25)" }} />
                }
                type="text"
                placeholder="Protagonist"
                data-test="SignupForm.LastName"
              />
            )}
          </Form.Item>
        </Col>
      </Row>
      <Row>
        <Col span={24}>
          <Form.Item label="Password">
            {form.getFieldDecorator("password", {
              validateTrigger: false,
              rules: [{ validator: passwordStrengthValidator }],
            })(
              <PasswordInput
                prefix={
                  <Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />
                }
                type="password"
                placeholder="correctbatteryhorsestaple"
                data-test="SignupForm.Password"
                strengthMeter
              />
            )}
          </Form.Item>
        </Col>
      </Row>
      <Form.Item>
        <Button
          block
          type="primary"
          htmlType="submit"
          disabled={submitting}
          data-test="SignupForm.Submit"
        >
          {submitting ? "Creating your account..." : "Create an Account"}
        </Button>
      </Form.Item>
    </Form>
  )
}

export default SignupForm
