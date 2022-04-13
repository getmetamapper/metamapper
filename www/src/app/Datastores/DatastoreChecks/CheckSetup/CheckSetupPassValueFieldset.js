import React, { Component } from "react"
import { Card, Form, Select } from "antd"
import { map } from "lodash"
import FormLabel from "app/Common/FormLabel"
import CheckSetupHandlerFieldset from "./CheckSetupHandlerFieldset"

class CheckSetupPassValueFieldset extends Component {
  constructor(props) {
    super(props);

    this.state = {
      handler: props.handler,
    }
  }

  setPassValueHandler = (handler) => {
    this.setState({ handler })
    this.props.onSelect(handler)
  }

  render() {
    const { handler } = this.state
    const { form, handlerOptions, queryColumns } = this.props
    return (
      <Card>
        <Form.Item>
          <FormLabel
            label="Type"
            helpText=""
            helpPlacement="left"
          />
          {form.getFieldDecorator(
            "passValueClass",
            {
              rules: [{ required: true, message: "This field is required." }],
            }
          )(
            <Select>
              {map(handlerOptions, (option) => (
                <Select.Option
                  value={option.handler}
                  key={option.handler}
                  onClick={() => this.setPassValueHandler(option)}
                >
                  {option.info}
                </Select.Option>
              ))}
            </Select>
          )}
        </Form.Item>
        {handler && (
          <CheckSetupHandlerFieldset
            form={form}
            field="passValueInput"
            queryColumns={queryColumns}
            handler={handler}
          />
        )}
      </Card>
    )
  }
}

export default CheckSetupPassValueFieldset
