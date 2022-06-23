import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import IntegrationConfigSetupForm from "./IntegrationConfigSetupForm"
import CreateIntegrationConfigMutation from "graphql/mutations/CreateIntegrationConfig"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class IntegrationConfigSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const { integration } = this.props
      const payload = {
        variables: {
          integration: integration.id,
          ...variables,
        },
        successMessage: "Integration has been created.",
        refetchQueries: [
          "GetIntegrationConfigs"
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.createIntegrationConfig

    if (!errors || errors.length <= 0) {
      this.props.onCancel()
      this.props.form.resetFields()
    }
  }

  handleCancel = () => {
    this.props.onCancel()
    this.props.form.resetFields()
  }

  render() {
    const { form, integration, submitting, visible } = this.props
    return (
      <Modal
        title={`Create New ${integration.name} Integration`}
        visible={visible}
        onCancel={this.handleCancel}
        footer={null}
      >
        <IntegrationConfigSetupForm
          form={form}
          integration={integration}
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
        />
      </Modal>
    )
  }
}

export default compose(
  Form.create(),
  graphql(CreateIntegrationConfigMutation),
  withGraphQLMutation,
)(IntegrationConfigSetup)
