import React from "react"
import { Select, Form } from "antd"
import { map } from "lodash"
import RestrictedButton from "app/Common/RestrictedButton"

const SetDefaultSSOConnectionForm = ({
  form: { getFieldDecorator },
  ssoConnections,
  defaultConnectionId,
  hasPermission,
  onSubmit,
  isSubmitting,
}) => (
  <Form layout="horizontal" onSubmit={onSubmit} data-test="SetDefaultSSOConnectionForm">
    <Form.Item>
      {getFieldDecorator("connection", {
        initialValue: defaultConnectionId,
      })(
        <Select disabled={!hasPermission} style={{ width: 400 }} data-test="SetDefaultSSOConnectionForm.Input">
          <Select.Option value={null}>No default connection</Select.Option>
          {map(ssoConnections, ({ pk, name }) => (
            <Select.Option key={pk} value={pk}>
              {name}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="SetDefaultSSOConnectionForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Set Default Connection"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default SetDefaultSSOConnectionForm
