import React from "react"
import { Form } from "antd"
import { arrayOfEmailsValidator } from "lib/validators"
import FormLabel from "app/Common/FormLabel"
import TagsInput from "app/Common/TagsInput"

const EmailChannelConfiguration = ({ form, channelConfig, hasPermission, }) => (
  <Form.Item>
    <div className="form-label-wrapper">
      <FormLabel label="Emails" required />
      <small>
        Where we should send the alert.
      </small>
    </div>
    {form.getFieldDecorator("channelConfig.emails", {
      initialValue: channelConfig.emails,
      rules: [
        { validator: arrayOfEmailsValidator },
      ],
    })(
      <TagsInput
        className="full-width"
        disabled={!hasPermission}
        data-test="EmailChannelConfiguration.IncidentContacts"
      />
    )}
  </Form.Item>
);

EmailChannelConfiguration.defaultProps = {
  channelConfig: { emails: [] },
};

const configurationMapping = {
  EMAIL: EmailChannelConfiguration,
};

const CheckAlertRuleConfiguration = ({
  form,
  rule,
  hasPermission,
}) => {
  const channel = form.getFieldValue("channel")
  console.log(rule)
  const ConfigurationComponent = configurationMapping[channel]
  return (
    <ConfigurationComponent
      form={form}
      channel={channel}
      channelConfig={rule.channelConfig}
      hasPermission={hasPermission}
    />
  )
};

CheckAlertRuleConfiguration.defaultProps = {
  hasPermission: false,
};

export default CheckAlertRuleConfiguration
