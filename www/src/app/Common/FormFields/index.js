import React, { Fragment } from "react"
import { map } from "lodash"
import { Input, InputNumber, Select } from "antd"
import TagsInput from "app/Common/TagsInput"

export const ChoiceField = ({ form, name, initialValue, isRequired, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
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

export const CharField = ({ form, name, initialValue, isRequired, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
    })(
      <Input type="text" />
    )}
  </Fragment>
)

export const ColumnField = ({ form, name, initialValue, isRequired, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
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


export const ColumnsField = ({ form, name, initialValue, isRequired, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
    })(
      <Select mode="multiple">
        {map(queryColumns, (choice) => (
          <Select.Option value={choice}>
            {choice}
          </Select.Option>
        ))}
      </Select>
    )}
  </Fragment>
)

export const IntegerField = ({ form, name, initialValue, isRequired, options, queryColumns }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
    })(
      <InputNumber />
    )}
  </Fragment>
)

export const BooleanField = ({ form, name, initialValue, isRequired, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
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

export const EmailsField = ({ form, name, initialValue, isRequired, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
    })(
      <TagsInput className="full-width" />
    )}
  </Fragment>
)

export const IntegrationField = ({ form, name, initialValue, isRequired, options }) => (
  <Fragment>
    {form.getFieldDecorator(name, {
      initialValue,
      rules: [
        { required: isRequired, message: "This field is required." },
      ],
    })(
      <Select>
        {options.map(({ label, value }) => (
          <Select.Option value={value}>{label}</Select.Option>
        ))}
      </Select>
    )}
  </Fragment>

)

export default {
  'BooleanField': BooleanField,
  'CharField': CharField,
  'ChoiceField': ChoiceField,
  'ColumnField': ColumnField,
  'ColumnsField': ColumnsField,
  'EmailsField': EmailsField,
  'IntegerField': IntegerField,
  'IntegrationField': IntegrationField,
}
