import React from "react"
import { Form, Input } from "antd"
import FormLabel from "app/Common/FormLabel"

const GroupFieldset = ({
  form,
  group: { name, description },
}) => (
  <>
    <Form.Item>
      <FormLabel required label="Name" />
      {form.getFieldDecorator("name", {
        initialValue: name,
        rules: [
          {
            required: true,
            message: "This field is required.",
          },
          {
            max: 30,
            message: "This field must be less than 30 characters.",
          },
        ],
      })(<Input type="text" data-test="GroupFieldset.Name" />)}
    </Form.Item>
    <Form.Item>
      <FormLabel
        label="Description"
        helpText="Short description to give context to your users."
      />
      {form.getFieldDecorator("description", {
        initialValue: description,
        rules: [
          {
            max: 60,
            message: "This field must be less than 60 characters.",
          },
        ],
      })(<Input type="text" data-test="GroupFieldset.Description" />)}
    </Form.Item>
  </>
)

GroupFieldset.defaultProps = {
  group: {},
}

export default GroupFieldset
