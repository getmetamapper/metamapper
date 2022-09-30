import React from "react"
import { Button, Divider, Form } from "antd"
import { find } from "lodash"
import CheckAlertRuleConfiguration from "app/Common/DynamicFieldset"
import CheckAlertRuleFieldset from "app/Datastores/DatastoreChecks/CheckAlertRuleFieldset"
import Link from "app/Navigation/Link"
import RestrictedButton from "app/Common/RestrictedButton"

const CheckAlertRuleEditForm = ({
  check,
  checkAlertRule,
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
        isEditMode
        form={form}
        rule={checkAlertRule}
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
        field="channelConfig"
        data={checkAlertRule.channelConfig}
        handler={find(channelOptions, (r => r.handler === checkAlertRule.channel))}
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
          data-test="CheckAlertRuleEditForm.Submit"
        >
          {isSubmitting ? "Saving..." : "Update Rule"}
        </RestrictedButton>
      </Form.Item>

    </div>
  </Form>
)

export default CheckAlertRuleEditForm
