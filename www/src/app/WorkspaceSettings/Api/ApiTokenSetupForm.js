import React from "react"
import FormLabel from "app/Common/FormLabel"
import { Button, Form, Input } from "antd"

const ApiTokenSetupForm = ({
  form: { getFieldDecorator },
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="api-token-setup-form">
    <Form.Item>
      <FormLabel label="Nickname" required />
      {getFieldDecorator("name", {
        rules: [{ required: true, message: "Please enter a name." }],
      })(
        <Input
          type="text"
          data-test="ApiTokenSetupForm.Name"
        />
      )}
    </Form.Item>
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        data-test="ApiTokenSetupForm.Submit"
      >
        {isSubmitting ? "Creating..." : "Create API Token"}
      </Button>
    </Form.Item>
  </Form>
)

export default ApiTokenSetupForm
