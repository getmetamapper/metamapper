import React from "react"
import FormLabel from "app/Common/FormLabel"
import { useTranslation } from "react-i18next"
import { Button, Form, Icon, Input, Switch } from "antd"

const WorkspaceSetupForm = ({
  form: { getFieldDecorator },
  isSubmitting,
  onSubmit,
  hasBeaconActivated,
}) => {
  const { t } = useTranslation();
  return (
    <Form onSubmit={onSubmit} className="workspace-setup-form">
      <Form.Item>
        <FormLabel label="Nickname" required />
        {getFieldDecorator("name", {
          rules: [{ required: true, message: "Please enter a name." }],
        })(
          <Input
            prefix={<Icon type="team" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="text"
            placeholder="Acme Corporation"
            data-test="WorkspaceSetupForm.Name"
          />
        )}
      </Form.Item>
      <Form.Item>
        <FormLabel
          label="Slug"
          helpText="The slug is used as part of the URL to access your workspace."
          required
        />
        {getFieldDecorator("slug", {
          rules: [{ required: true, message: "Please enter a slug." }],
        })(
          <Input
            prefix={<Icon type="link" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="text"
            placeholder="acme"
            data-test="WorkspaceSetupForm.Slug"
          />
        )}
      </Form.Item>
      {hasBeaconActivated && (
        <Form.Item>
          <FormLabel label="Usage Statistics" />
          {getFieldDecorator("beaconConsent", {
            initialValue: false,
          })(
              <Switch data-test="WorkspaceSetupForm.BeaconConsent" />
          )}
          <p className="mb-0">
            {t("beacon.prompt")} <a target="_blank" rel="noopener noreferrer" href={t("beacon.docsUrl")}>{t("Learn more")}.</a>
          </p>
        </Form.Item>
      )}
      <Form.Item>
        <Button
          block
          type="primary"
          htmlType="submit"
          data-test="WorkspaceSetupForm.Submit"
        >
          {isSubmitting ? "Creating..." : "Create Workspace"}
        </Button>
      </Form.Item>
    </Form>
  )
}

export default WorkspaceSetupForm
