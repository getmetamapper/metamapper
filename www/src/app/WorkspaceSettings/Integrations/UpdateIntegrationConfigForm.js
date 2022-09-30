import React from "react"
import { Button, Form } from "antd"
import DynamicFieldset from "app/Common/DynamicFieldset"

const UpdateIntegrationConfigForm = ({
  integration,
  integrationConfig,
  form,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="integration-form" data-test="UpdateIntegrationConfigForm">
    <DynamicFieldset
      form={form}
      field="meta"
      handler={integration}
      data={{
        // eslint-disable-next-line
        ...integrationConfig.authKeys.reduce((a, c) => (a[c] = "<redacted>", a), {}),
        ...integrationConfig.meta
      }}
    />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="UpdateIntegrationConfigForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Update Integration"}
      </Button>
    </Form.Item>
  </Form>
)

export default UpdateIntegrationConfigForm
