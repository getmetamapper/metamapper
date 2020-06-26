import React from "react"
import qs from "query-string"
import { Form, Icon, Input, Button, Row, Divider, Col } from "antd"
import PasswordInput from "app/Common/PasswordInput"
import { passwordStrengthValidator } from "lib/validators"

const AccountSetupForm = ({
  form,
  origin,
  onSubmit,
  submitting,
}) => (
  <Form onSubmit={onSubmit} className="signup-form">
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
              data-test="AccountSetupForm.FirstName"
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
              data-test="AccountSetupForm.LastName"
            />
          )}
        </Form.Item>
      </Col>
    </Row>
    <Row>
      <Col span={24}>
        <Form.Item label="Email Address">
          {form.getFieldDecorator("email", {
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
              data-test="AccountSetupForm.Email"
            />
          )}
        </Form.Item>
      </Col>
    </Row>
    <Row>
      <Col span={24}>
        <Form.Item label="Password">
          {form.getFieldDecorator("password", {
            rules: [{ validator: passwordStrengthValidator }],
          })(
            <PasswordInput
              prefix={
                <Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />
              }
              type="password"
              data-test="AccountSetupForm.Password"
              strengthMeter
            />
          )}
        </Form.Item>
      </Col>
    </Row>
    <Row>
      <Col span={24}>
        <Form.Item label="Organization Name">
          {form.getFieldDecorator("workspaceName", {
            rules: [
              {
                required: true,
                message: "This field is required.",
              },
            ],
          })(
            <Input
              prefix={
                <Icon type="bank" style={{ color: "rgba(0,0,0,.25)" }} />
              }
              type="text"
              data-test="AccountSetupForm.WorkspaceName"
            />
          )}
        </Form.Item>
      </Col>
    </Row>
    <Row>
      <Col span={24}>
        <Form.Item label="URL Identifier">
          {form.getFieldDecorator("workspaceSlug", {
            rules: [
              {
                required: true,
                message: "This field is required.",
              },
            ],
          })(
            <Input
              type="text"
              addonBefore={window.location.origin + "/"}
              data-test="AccountSetupForm.WorkspaceSlug"
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
        data-test="AccountSetupForm.Submit"
      >
        {submitting ? "Creating your account..." : "Create Account"}
      </Button>
    </Form.Item>
  </Form>
)

export default AccountSetupForm
