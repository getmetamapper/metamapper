import React from "react"
import { Select } from "antd"
import { map } from "lodash"

const MultiSelectInput = ({ form, initialValue, field: { pk }, choices }) => (
  <>
    {form.getFieldDecorator(pk, { initialValue: initialValue || [] })(
      <Select mode="multiple" data-test={`CustomProperties.Input(${pk})`}>
        {map(choices, (choice) => (
          <Select.Option key={choice} value={choice}>
            {choice}
          </Select.Option>
        ))}
      </Select>
    )}
  </>
)

MultiSelectInput.defaultProps = {
  choices: [],
}

export default MultiSelectInput
