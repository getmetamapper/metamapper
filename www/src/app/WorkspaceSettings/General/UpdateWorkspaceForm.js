import React from "react"
import { Form, Input, Col, Row } from "antd"
import FormLabel from "app/Common/FormLabel"
import RestrictedButton from "app/Common/RestrictedButton"

const UpdateWorkspaceForm = ({
  workspace,
  form: { getFieldDecorator },
  isSubmitting,
  onSubmit,
  hasPermission,
}) => (
  <Form onSubmit={onSubmit} className="update-workspace-form">
    <Row>
      <Col span={12}>
        <fieldset disabled={!hasPermission}>
          <Form.Item>
            <FormLabel
              required
              label="Display Name"
              helpText="This is the name that users will see for the workspace."
            />
            {getFieldDecorator("name", {
              initialValue: workspace.name,
              rules: [{ required: true, message: "This field is required." }],
            })(<Input type="text" disabled={!hasPermission} data-test="UpdateWorkspaceForm.Name" />)}
          </Form.Item>
          <Form.Item>
            <FormLabel
              required
              label="Slug"
              helpText="A unique ID used to identify this workspace."
            />
            {getFieldDecorator("slug", {
              initialValue: workspace.slug,
              rules: [{ required: true, message: "This field is required." }],
            })(<Input type="text" disabled={!hasPermission} data-test="UpdateWorkspaceForm.Slug" />)}
          </Form.Item>
          <Form.Item className="hidden">
            {getFieldDecorator("id", { initialValue: workspace.id })(
              <Input type="text" hidden />
            )}
          </Form.Item>
          <Form.Item>
            <RestrictedButton
              type="primary"
              htmlType="submit"
              hasPermission={hasPermission}
              isSubmitting={isSubmitting}
              data-test="UpdateWorkspaceForm.Submit"
            >
              {isSubmitting ? "Saving..." : "Save Changes"}
            </RestrictedButton>
          </Form.Item>
        </fieldset>
      </Col>
    </Row>
  </Form>
)

export default UpdateWorkspaceForm
