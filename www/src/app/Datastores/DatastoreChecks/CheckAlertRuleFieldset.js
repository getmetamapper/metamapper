import React, { Fragment } from "react"
import FormLabel from "app/Common/FormLabel"
import { Form, Input, Select } from "antd"

const CheckAlertRuleFieldset = ({
  form: { getFieldDecorator },
  isEditMode,
  channelOptions,
  intervalOptions,
  hasPermission,
  rule,
}) => (
  <Fragment>
    <Form.Item>
      <div className="form-label-wrapper">
        <FormLabel label="Name" required />
        <small>
          Add a name for this alert.
        </small>
      </div>
      {getFieldDecorator("name", {
        initialValue: rule.name,
        rules: [{ required: true, message: "Please enter a name." }],
      })(
        <Input
          type="text"
          placeholder="My Rule Name"
          data-test="CheckAlertRuleFieldset.Name"
        />
      )}
    </Form.Item>
    <Form.Item>
      <div className="form-label-wrapper">
        <FormLabel label="Channel" required />
        <small>
          Deliver the alert via this provider.
        </small>
      </div>
      {getFieldDecorator("channel", {
        initialValue: rule.channel,
        rules: [{ required: true, message: "Please select a channel." }],
      })(
        <Select
          type="text"
          disabled={!hasPermission || isEditMode}
          data-test="CheckAlertRuleFieldset.Channel"
        >
          {channelOptions.map(({ name, handler }) => (
            <Select.Option key={handler}>
              {name}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
    <Form.Item>
      <div className="form-label-wrapper">
        <FormLabel required label="Action Interval" />
        <small>
          Perform the alert once this often for a failed check.
        </small>
      </div>
      {getFieldDecorator("interval", {
        initialValue: rule.interval.value,
        rules: [{ required: true, message: "Please select an action interval." }],
      })(
        <Select
          type="text"
          disabled={!hasPermission}
          data-test="CheckAlertRuleFieldset.ScheduleInterval"
        >
          {intervalOptions.map(({ label, value }) => (
            <Select.Option key={value}>
              {label}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
  </Fragment>
)

CheckAlertRuleFieldset.defaultProps = {
  hasPermission: false,
  isEditMode: false,
  rule: {
    channel: "EMAIL",
    interval: { value: "0:30:00" },
  },
}

export default CheckAlertRuleFieldset
