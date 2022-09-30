import React from "react"
import { Form } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"
import DatastoreSettingsFieldset from "./DatastoreSettingsFieldset"

const DatastoreSettingsForm = ({
  datastore,
  datastoreIntervalOptions,
  form,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="datastore-settings-form">
    <DatastoreSettingsFieldset
      form={form}
      datastore={datastore}
      datastoreIntervalOptions={datastoreIntervalOptions}
      hasPermission={hasPermission}
    />
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        isSubmitting={isSubmitting}
        data-test="DatastoreSettingsForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Save Datastore"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default DatastoreSettingsForm
