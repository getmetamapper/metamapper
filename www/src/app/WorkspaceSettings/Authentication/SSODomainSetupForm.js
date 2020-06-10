import React from "react"
import { Input, Form } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"

const SSODomainSetupForm = ({
  form: { getFieldDecorator },
  hasPermission,
  onSubmit,
  isSubmitting,
}) => (
  <Form layout="inline" onSubmit={onSubmit}>
    <Form.Item>
      {getFieldDecorator(
        "domain",
        {}
      )(
        <Input
          type="text"
          placeholder="e.g., example.com"
          disabled={!hasPermission}
          data-test="SSODomainSetupForm.Domain"
        />
      )}
    </Form.Item>
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="SSODomainSetupForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Add Domain"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default SSODomainSetupForm
