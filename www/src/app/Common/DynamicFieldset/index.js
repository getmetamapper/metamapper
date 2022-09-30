import React, { Fragment } from "react"
import { Form } from "antd"
import { map } from "lodash"
import { tryGetValue } from "lib/utilities"
import FormLabel from "app/Common/FormLabel"
import fieldMapping from "app/Common/FormFields"

const DynamicFieldset = ({ form, field, data, handler }) => (
  <Fragment>
    {handler && (
      <Fragment>
        {map(handler.details, ({ name, label, type, helpText, isRequired, options }) => {
          const Component = fieldMapping[type]
          const error = form.getFieldError(`${field}.${name}`)
          return (
            <Form.Item key={name}>
              <div className="form-label-wrapper">
                <FormLabel label={label} required={isRequired} />
                <small>{helpText}</small>
              </div>
              <div className={error ? 'has-error' : ''}>
                <Component
                  initialValue={tryGetValue(data, name)}
                  form={form}
                  name={`${field}.${name}`}
                  options={options}
                  isRequired={isRequired}
                />
              </div>
              {error && (
                <div className="ant-form-explain" style={{ color: '#faad14' }}>
                  {error}
                </div>
              )}
            </Form.Item>
          )
        })}
      </Fragment>
    )}
  </Fragment>
)

export default DynamicFieldset
