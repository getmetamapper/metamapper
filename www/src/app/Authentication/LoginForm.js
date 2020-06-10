import React from "react"
import qs from "query-string"
import { Link } from "react-router-dom"
import { Button, Input, Icon, Form, Divider } from "antd"

const LoginForm = ({ form, onSubmit, submitting }) => {
  const { email } = qs.parse(window.location.search)
  return (
    <Form className="login-form" onSubmit={onSubmit}>
      <Divider />
      <Form.Item label="Email Address">
        {form.getFieldDecorator("email", {
          initialValue: email || "",
        })(
          <Input
            prefix={<Icon type="mail" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="email"
            placeholder="hiro.protagonist@metaverse.io"
            data-test="LoginForm.Email"
            required
          />
        )}
      </Form.Item>
      <Form.Item label="Password">
        {form.getFieldDecorator(
          "password",
          {}
        )(
          <Input
            prefix={<Icon type="lock" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="password"
            placeholder="correctbatteryhorsestaple"
            data-test="LoginForm.Password"
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
          data-test="LoginForm.Submit"
        >
          {submitting ? "Signing you in..." : "Sign In"}
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

export default LoginForm
