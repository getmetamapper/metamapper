import React from "react"
import { Form } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"
import ConnectionSettingsFieldset from "./ConnectionSettingsFieldset"

const ConnectionSettingsForm = ({
  datastore,
  form,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="connection-settings-form">
    <ConnectionSettingsFieldset
      engine={datastore.jdbcConnection.engine}
      form={form}
      datastore={datastore}
      publicKey={datastore.sshConfig.publicKey}
      hasPermission={hasPermission}
    />
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="ConnectionSettingsForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Save Connection"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default ConnectionSettingsForm
