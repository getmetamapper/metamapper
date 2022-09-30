import React from "react"
import { Card, Col, Form, Input, Row, Select, Switch } from "antd"
import FormLabel from "app/Common/FormLabel"
import TagsInput from "app/Common/TagsInput"

const ChecksFieldset = ({
  check,
  checkIntervalOptions,
  form: { getFieldDecorator },
  hasPermission,
}) => (
  <>
    <Form.Item>
      <FormLabel required label="Name" />
      {getFieldDecorator("name", {
        initialValue: check.name,
        rules: [{ required: true, message: "This field is required." }],
      })(
        <Input
          type="text"
          disabled={!hasPermission}
          data-test="CheckFieldset.Name"
        />
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Tags" />
      {getFieldDecorator("tags", {
        initialValue: check.tags,
        rules: [],
      })(
        <TagsInput
          className="full-width"
          disabled={!hasPermission}
          data-test="CheckFieldset.Tags"
        />
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Description" />
      {getFieldDecorator("shortDesc", {
        initialValue: check.shortDesc,
        rules: [],
      })(
        <Input.TextArea
          type="text"
          disabled={!hasPermission}
          data-test="CheckFieldset.Name"
        />
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel required label="Schedule Interval" />
      {getFieldDecorator("interval", {
        initialValue: check.interval.value,
        rules: [],
      })(
        <Select
          type="text"
          disabled={!hasPermission}
          data-test="CheckFieldset.ScheduleInterval"
        >
          {checkIntervalOptions.map(({ label, value }) => (
            <Select.Option key={value}>
              {label}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
    {check && check.hasOwnProperty("isEnabled") && (
      <Form.Item>
        <Card className="check-enabled">
          <Row>
            <Col span={18}>
              <span className="label">Enabled</span>
              <small>
                No queries will be executed when this check is disabled.
              </small>
            </Col>
            <Col span={6}>
              <span className="pull-right">
                {getFieldDecorator("isEnabled", {
                  initialValue: check.isEnabled,
                  rules: [],
                })(
                  <Switch
                    defaultChecked={check.isEnabled}
                    disabled={!hasPermission}
                    data-test="CheckFieldset.Enabled"
                  />
                )}
              </span>
            </Col>
          </Row>
        </Card>
      </Form.Item>
    )}
  </>
)

ChecksFieldset.defaultProps = {
  check: { interval: { value: "1:00:00" } },
}

export default ChecksFieldset
