import React from "react"
import { Button, Form } from "antd"
import GroupFieldset from "./GroupFieldset"

const GroupSetupForm = ({ form, isSubmitting, onSubmit }) => (
  <Form onSubmit={onSubmit} className="group-setup-form" data-test="GroupSetupForm">
    <GroupFieldset form={form} />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="GroupSetupForm.Submit"
      >
        {isSubmitting ? "Creating..." : "Create Group"}
      </Button>
    </Form.Item>
  </Form>
)

export default GroupSetupForm
