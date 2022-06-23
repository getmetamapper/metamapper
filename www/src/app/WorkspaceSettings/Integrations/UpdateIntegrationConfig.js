import React, { Component, Fragment } from "react"
import { graphql, compose } from "react-apollo"
import { Button, Form, Modal } from "antd"
import UpdateIntegrationConfigForm from "app/WorkspaceSettings/Integrations/UpdateIntegrationConfigForm"
import UpdateIntegrationConfigMutation from "graphql/mutations/UpdateIntegrationConfig"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateIntegrationConfig extends Component {
  state = { visible: false }

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const { integrationConfig: { id } } = this.props
      const { meta } = variables
      const payload = {
        variables: {
          id,
          meta,
        },
        successMessage: "Integration has been updated.",
        refetchQueries: [
          "GetIntegrationConfigs"
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.updateIntegrationConfig

    if (!errors || errors.length <= 0 ) {
      this.props.form.resetFields()
      this.handleCancel()
    }
  }

  handleCancel = () => {
    this.setState({ visible: false })
  }

  render() {
    const {
      form,
      integration,
      integrationConfig,
      hasPermission,
      submitting,
    } = this.props
    const { visible } = this.state
    return (
      <Fragment>
        <Modal
          title={`Update ${integration.name} Integration`}
          visible={visible}
          onCancel={this.handleCancel}
          footer={null}
        >
          <UpdateIntegrationConfigForm
            integration={integration}
            integrationConfig={integrationConfig}
            form={form}
            onSubmit={this.handleSubmit}
            isSubmitting={submitting}
          />
        </Modal>
        <Button
          type="primary"
          shape="circle"
          icon="setting"
          size="small"
          disabled={!hasPermission}
          style={{ marginRight: 8 }}
          onClick={() => this.setState({ visible: true })}
        />
      </Fragment>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  graphql(UpdateIntegrationConfigMutation),
  withGraphQLMutation
)

export default enhance(UpdateIntegrationConfig)
