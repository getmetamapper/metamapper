import React, { Fragment } from "react"
import { map } from "lodash"
import { Input, InputNumber, Select } from "antd"

export const ChoiceField = ({ form, name, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      rules: [{ required: true, message: "This field is required." }],
    })(
      <Select>
        {map(options.choices, (choice) => (
          <Select.Option value={choice}>
            {choice}
          </Select.Option>
        ))}
      </Select>
    )}
  </Fragment>
)

export const CharField = ({ form, name, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      rules: [{ required: true, message: "This field is required." }],
    })(
      <Input type="text" />
    )}
  </Fragment>
)

export const ColumnField = ({ form, name, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      rules: [{ required: true, message: "This field is required." }],
    })(
      <Select>
        {map(queryColumns, (choice) => (
          <Select.Option value={choice}>
            {choice}
          </Select.Option>
        ))}
      </Select>
    )}
  </Fragment>
)

export const IntegerField = ({ form, name, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      rules: [{ required: true, message: "This field is required." }],
    })(
      <InputNumber />
    )}
  </Fragment>
)

export const BooleanField = ({ form, name, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      rules: [{ required: true, message: "This field is required." }],
    })(
      <Select>
        <Select.Option value={true}>
          True
        </Select.Option>
        <Select.Option value={false}>
          False
        </Select.Option>
      </Select>
    )}
  </Fragment>
)

export default {
  'BooleanField': BooleanField,
  'CharField': CharField,
  'ChoiceField': ChoiceField,
  'ColumnField': ColumnField,
  'IntegerField': IntegerField,
}
