import React from "react"
import { Select } from "antd"
import { map } from "lodash"

const EnumInput = ({ form, initialValue, field: { pk }, choices }) => (
  <>
    {form.getFieldDecorator(pk, { initialValue })(
      <Select data-test={`CustomProperties.Input(${pk})`}>
        {map(choices, (choice) => (
          <Select.Option key={choice} value={choice}>
            {choice}
          </Select.Option>
        ))}
        <Select.Option key={""} value={""}>
          (reset this property)
        </Select.Option>
      </Select>
    )}
  </>
)

EnumInput.defaultProps = {
  choices: [],
}

export default EnumInput
