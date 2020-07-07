import React from "react"
import { Button, Form } from "antd"
import GroupFieldset from "./GroupFieldset"

const UpdateGroupForm = ({
  group,
  form,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="group-update-form" data-test="UpdateGroupForm">
    <GroupFieldset form={form} group={group} />
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="UpdateGroupForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Update Group"}
      </Button>
    </Form.Item>
  </Form>
)

export default UpdateGroupForm
