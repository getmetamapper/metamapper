import React from "react"
import { Input } from "antd"

const TextInput = ({ form, initialValue, field: { pk, validators } }) => (
  <>
    {form.getFieldDecorator(pk, { initialValue })(
        <Input type="text" data-test={`CustomProperties.Input(${pk})`} />
    )}
  </>
)

export default TextInput
