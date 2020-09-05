import React from "react"
import { Button, Form } from "antd"
import CustomFieldFieldset from "./CustomFieldFieldset"

const CustomFieldSetupForm = ({ form, isSubmitting, onSubmit }) => (
  <Form onSubmit={onSubmit} className="customfield-setup-form" data-test="CustomFieldSetupForm">
    <CustomFieldFieldset form={form} />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="CustomFieldSetupForm.Submit"
      >
        {isSubmitting ? "Creating..." : "Create Custom Property"}
      </Button>
    </Form.Item>
  </Form>
)

export default CustomFieldSetupForm
