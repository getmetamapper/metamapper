import React from "react"
import qs from "query-string"
import { Link } from "react-router-dom"
import { Button, Input, Icon, Form, Divider } from "antd"

const LoginPromptForm = ({ form, onSubmit, submitting }) => {
  const { email } = qs.parse(window.location.search)
  return (
    <Form className="login-prompt-form" onSubmit={onSubmit}>
      <Divider />
      <Form.Item>
        {form.getFieldDecorator("email", {
          initialValue: email || "",
        })(
          <Input
            prefix={<Icon type="mail" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="email"
            placeholder="hiro.protagonist@metaverse.io"
            data-test="LoginPromptForm.Email"
          />
        )}
      </Form.Item>
      <Form.Item>
        <Button
          block
          type="primary"
          htmlType="submit"
          disabled={submitting}
          data-test="LoginPromptForm.Submit"
        >
          {submitting ? "One moment..." : "Continue with Email"}
        </Button>
      </Form.Item>
      <Divider />
      <Form.Item>
        <Link to="/login/sso">
          <Button block type="default">
            <Icon type="lock" /> Sign In with Single Sign-On
          </Button>
        </Link>
      </Form.Item>
    </Form>
  )
}

export default LoginPromptForm
