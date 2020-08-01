import React from "react"
import { Form, Input, Select } from "antd"
import { map, get } from "lodash"
import FormLabel from "app/Common/FormLabel"
import TagsInput from "app/Common/TagsInput"

const EnumTypeFieldset = ({ form, validators }) => (
  <Form.Item>
    <FormLabel
      required
      label="Available Choices"
      helpText="This field will be restricted to only these provided values."
    />
    {form.getFieldDecorator("validators.choices", {
      initialValue: validators.choices,
      rules: [
        {
          required: true,
          message: "This field is required.",
        },
      ],
    })(<TagsInput className="full-width" data-test="CustomFieldFieldset.EnumChoices" />)}
  </Form.Item>
)

EnumTypeFieldset.defaultProps = {
  validators: {},
}

const fieldsetMapping = {
  ENUM: EnumTypeFieldset,
  TEXT: null,
  USER: null,
  GROUP: null,
}

const CustomFieldFieldset = ({
  form,
  customField: { fieldName, fieldType, shortDesc, validators },
}) => {
  const FieldsetComponent = get(
    fieldsetMapping,
    form.getFieldValue("fieldType") || fieldType,
    null
  )
  return (
    <>
      <Form.Item>
        <FormLabel required label="Name" />
        {form.getFieldDecorator("fieldName", {
          initialValue: fieldName,
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
        })(<Input type="text" data-test="CustomFieldFieldset.Name" />)}
      </Form.Item>
      <Form.Item>
        <FormLabel
          label="Description"
          helpText="Short description to give context to your users."
        />
        {form.getFieldDecorator("shortDesc", {
          initialValue: shortDesc,
          rules: [
            {
              max: 60,
              message: "This field must be less than 60 characters.",
            },
          ],
        })(<Input type="text" data-test="CustomFieldFieldset.Description" />)}
      </Form.Item>
      <Form.Item>
        <FormLabel required label="Type" />
        {form.getFieldDecorator("fieldType", {
          initialValue: fieldType || "TEXT",
          rules: [
            {
              required: true,
              message: "This field is required.",
            },
          ],
        })(
          <Select disabled={fieldType !== undefined} data-test="CustomFieldFieldset.Type">
            {map(Object.keys(fieldsetMapping), (type) => (
              <Select.Option key={type} value={type}>
                {type}
              </Select.Option>
            ))}
          </Select>
        )}
      </Form.Item>
      {FieldsetComponent && (
        <FieldsetComponent form={form} validators={validators} />
      )}
    </>
  )
}

CustomFieldFieldset.defaultProps = {
  customField: {},
}

export default CustomFieldFieldset
