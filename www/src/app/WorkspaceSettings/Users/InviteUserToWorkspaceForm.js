import React from "react"
import { Input, Form, Select } from "antd"
import { DEFAULT_PERMISSION, PERMISSION_CHOICES } from "lib/constants"
import RestrictedButton from "app/Common/RestrictedButton"

const InviteUserToTeamForm = ({
  form: { getFieldDecorator },
  hasPermission,
  onSubmit,
  isSubmitting,
}) => (
  <Form layout="inline" onSubmit={onSubmit} data-test="InviteUserToTeamForm">
    <Form.Item>
      {getFieldDecorator(
        "email",
        {}
      )(
        <Input
          type="text"
          placeholder="e.g., bruton.gaster@sbpd.gov"
          disabled={!hasPermission}
          data-test="InviteUserToTeamForm.Email"
        />
      )}
    </Form.Item>
    <Form.Item>
      {getFieldDecorator("permissions", { initialValue: DEFAULT_PERMISSION })(
        <Select disabled={!hasPermission} data-test="InviteUserToTeamForm.Permissions">
          {Object.keys(PERMISSION_CHOICES).map((key, index) => (
            <Select.Option key={key} value={key}>
              {PERMISSION_CHOICES[key]}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="InviteUserToTeamForm.Submit"
      >
        {isSubmitting ? "Inviting..." : "Send invite"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default InviteUserToTeamForm
