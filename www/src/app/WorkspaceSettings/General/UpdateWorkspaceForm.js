import React from "react"
import { Form, Input, Col, Row, Switch } from "antd"
import { useTranslation } from "react-i18next"
import FormLabel from "app/Common/FormLabel"
import RestrictedButton from "app/Common/RestrictedButton"

const UpdateWorkspaceForm = ({
  workspace,
  form: { getFieldDecorator },
  isSubmitting,
  onSubmit,
  hasPermission,
  hasBeaconActivated,
}) => {
  const { t } = useTranslation()
  return (
    <Form onSubmit={onSubmit} className="update-workspace-form">
      <Row>
        <Col span={12}>
          <fieldset disabled={!hasPermission}>
            <Form.Item>
              <FormLabel
                required
                label="Display Name"
                helpText="This is the name that users will see for the workspace."
              />
              {getFieldDecorator("name", {
                initialValue: workspace.name,
                rules: [{ required: true, message: "This field is required." }],
              })(
                <Input
                  type="text"
                  disabled={!hasPermission}
                  data-test="UpdateWorkspaceForm.Name"
                />
              )}
            </Form.Item>
            <Form.Item>
              <FormLabel
                required
                label="Workspace Slug"
                helpText="A unique ID used to identify this workspace."
              />
              {getFieldDecorator("slug", {
                initialValue: workspace.slug,
                rules: [{ required: true, message: "This field is required." }],
              })(
                <Input
                  type="text"
                  disabled={!hasPermission}
                  data-test="UpdateWorkspaceForm.Slug"
                />
              )}
            </Form.Item>
            <Form.Item className="hidden">
              {getFieldDecorator("id", { initialValue: workspace.id })(
                <Input type="text" hidden />
              )}
            </Form.Item>
            <Form.Item>
              <FormLabel
                label="Application Key"
                helpText="Used for authentication against the API."
                required
              />
              {getFieldDecorator("id", { initialValue: workspace.pk })(
                <Input
                  type="text"
                  disabled
                  data-test="UpdateWorkspaceForm.ID"
                />
              )}
            </Form.Item>
            {hasBeaconActivated && (
              <Form.Item>
                <FormLabel label="Usage Statistics" />
                {getFieldDecorator("beaconConsent", {
                  initialValue: workspace.beaconConsent,
                })(
                    <Switch defaultChecked={workspace.beaconConsent} data-test="UpdateWorkspaceForm.BeaconConsent" />
                )}
                <p className="mb-0 mt-5">
                  {t("beacon.prompt")} <a target="_blank" rel="noopener noreferrer" href={t("beacon.docsUrl")}>{t("Learn more")}.</a>
                </p>
              </Form.Item>
            )}
            <Form.Item>
              <RestrictedButton
                type="primary"
                htmlType="submit"
                hasPermission={hasPermission}
                isSubmitting={isSubmitting}
                data-test="UpdateWorkspaceForm.Submit"
              >
                {isSubmitting ? "Saving..." : "Save Changes"}
              </RestrictedButton>
            </Form.Item>
          </fieldset>
        </Col>
      </Row>
    </Form>
  )
}

export default UpdateWorkspaceForm
