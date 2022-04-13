import React from "react"
import { Form } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"

const DatastoreNotificationSettingsForm = ({
  datastore,
  form,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="datastore-notification-settings-form">
    <p>
      Get notified when your datastore is not syncing properly.
    </p>
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="DatastoreNotificationSettingsForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Save Datastore"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default DatastoreNotificationSettingsForm
