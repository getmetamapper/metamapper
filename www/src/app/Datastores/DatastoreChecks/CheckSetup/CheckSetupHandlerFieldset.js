import React from "react"
import { Card, Form } from "antd"
import { map } from "lodash"
import FormLabel from "app/Common/FormLabel"
import fieldMapping from "./CheckSetupFields"

const CheckSetupHandlerFieldset = ({ form, field, queryColumns, handler }) => (
  <Card className="mb-16">
    {map(handler.details, ({ name, label, type, helpText, options }) => {
      const Component = fieldMapping[type]
      return (
        <Form.Item>
          <FormLabel
            label={label}
            helpText={helpText}
            helpPlacement="left"
          />
          <Component
            form={form}
            name={`${field}.${name}`}
            options={options}
            queryColumns={queryColumns}
          />
        </Form.Item>
      )
    })}
  </Card>
)

export default CheckSetupHandlerFieldset
