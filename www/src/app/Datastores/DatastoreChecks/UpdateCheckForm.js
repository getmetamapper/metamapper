import React from "react"
import { Form } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"
import CheckFieldset from "app/Datastores/DatastoreChecks/CheckFieldset"

const UpdateCheckForm = ({
  check,
  checkIntervalOptions,
  form,
  isSubmitting,
  onSubmit,
  hasPermission,
}) => (
  <Form onSubmit={onSubmit} className="update-check-form">
      <fieldset disabled={!hasPermission}>
        <CheckFieldset
          check={check}
          checkIntervalOptions={checkIntervalOptions}
          form={form}
          hasPermission={hasPermission}
        />
        <Form.Item>
          <RestrictedButton
            type="primary"
            htmlType="submit"
            hasPermission={hasPermission}
            isSubmitting={isSubmitting}
            data-test="UpdateCheckForm.Submit"
          >
            {isSubmitting ? "Saving..." : "Save Changes"}
          </RestrictedButton>
        </Form.Item>
      </fieldset>
  </Form>
)

export default UpdateCheckForm
