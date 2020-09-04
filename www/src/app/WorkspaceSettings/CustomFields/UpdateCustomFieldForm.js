import React from "react"
import { Button, Form } from "antd"
import CustomFieldFieldset from "./CustomFieldFieldset"

const UpdateCustomFieldForm = ({
  customField,
  form,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="customfield-setup-form" data-test="UpdateCustomFieldForm">
    <CustomFieldFieldset form={form} customField={customField} />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="UpdateCustomFieldForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Update Custom Property"}
      </Button>
    </Form.Item>
  </Form>
)

export default UpdateCustomFieldForm
