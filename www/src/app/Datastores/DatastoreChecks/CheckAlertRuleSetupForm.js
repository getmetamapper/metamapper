import React from "react"
import { Button, Divider, Form } from "antd"
import CheckAlertRuleConfiguration from "app/Datastores/DatastoreChecks/CheckAlertRuleConfiguration"
import CheckAlertRuleFieldset from "app/Datastores/DatastoreChecks/CheckAlertRuleFieldset"
import Link from "app/Navigation/Link"
import RestrictedButton from "app/Common/RestrictedButton"

const CheckAlertRuleSetupForm = ({
  check,
  datastore,
  form,
  channelOptions,
  intervalOptions,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="check-alert-rule-setup-form">
    <div className="mb-20">
      <h3>
        Alert settings
      </h3>
      <Divider />
      <CheckAlertRuleFieldset
        form={form}
        channelOptions={channelOptions}
        intervalOptions={intervalOptions}
        hasPermission={hasPermission}
      />
    </div>
    <div>
      <h3>
        Channel configuration
      </h3>
      <Divider />
      <CheckAlertRuleConfiguration
        form={form}
        rule={{
          channel: form.getFieldValue("channel"),
          channelConfig: {},
        }}
        hasPermission={hasPermission}
      />
    </div>
    <div className="mt-24 text-right">
      <Form.Item>
        <Link to={`/datastores/${datastore.slug}/checks/${check.pk}`}>
          <Button style={{ marginRight: 12 }}>
            Cancel
          </Button>
        </Link>
        <RestrictedButton
          type="primary"
          htmlType="submit"
          hasPermission={hasPermission}
          isSubmitting={isSubmitting}
          data-test="CheckAlertRuleSetupForm.Submit"
        >
          {isSubmitting ? "Saving..." : "Create Rule"}
        </RestrictedButton>
      </Form.Item>

    </div>
  </Form>
)

export default CheckAlertRuleSetupForm
