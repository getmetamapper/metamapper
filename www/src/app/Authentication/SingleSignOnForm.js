import React from "react"
import { Button, Input, Form, Divider } from "antd"

const SingleSignOnForm = ({ form, onSubmit, submitting }) => (
  <Form className="sso-form" onSubmit={onSubmit}>
    <Divider />
    <Form.Item
      label="Workspace Slug"
      help={
        <span>
          Your ID is the slug after the hostname. e.g. metamapper.io/acme/ is
          acme.
        </span>
      }
    >
      {form.getFieldDecorator(
        "workspaceSlug",
        {}
      )(<Input type="text" placeholder="acme" />)}
    </Form.Item>
    <Form.Item>
      <Button block type="primary" htmlType="submit" disabled={submitting}>
        {submitting ? "Working..." : "Continue"}
      </Button>
    </Form.Item>
  </Form>
)

export default SingleSignOnForm
