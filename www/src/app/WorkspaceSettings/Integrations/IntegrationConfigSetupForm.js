import React from "react"
import { Button, Form } from "antd"
import DynamicFieldset from "app/Common/DynamicFieldset"

const IntegrationConfigSetupForm = ({ form, integration, isSubmitting, onSubmit }) => (
  <Form onSubmit={onSubmit} className="integration-form" data-test="IntegrationConfigSetupForm">
    <DynamicFieldset
      form={form}
      field="meta"
      handler={integration}
    />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="IntegrationConfigSetupForm.Submit"
      >
        {isSubmitting ? "Creating..." : "Create Integration"}
      </Button>
    </Form.Item>
  </Form>
)

export default IntegrationConfigSetupForm
