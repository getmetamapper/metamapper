import React from "react"
import { Form, Select } from "antd"
import { map } from "lodash"
import { coalesce } from "lib/utilities"
import RestrictedButton from "app/Common/RestrictedButton"

const AddUserToGroupForm = ({
  users,
  form: { getFieldDecorator, getFieldValue },
  hasPermission,
  onSubmit,
  isSubmitting,
}) => (
  <Form onSubmit={onSubmit} className="add-user-to-group-form" data-test="AddUserToGroupForm">
    <Form.Item>
      {getFieldDecorator(
        "userId",
        {}
      )(
        <Select
          showSearch
          placeholder="Enter a team members name"
          data-test="AddUserToGroupForm.Input"
          filterOption={(input, option) =>
            option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
          }
         >
          {map(users, (user) => (
            <Select.Option value={user.userId}>
              {coalesce(user.name, user.email)}
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
        data-test="AddUserToGroupForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Submit"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default AddUserToGroupForm
