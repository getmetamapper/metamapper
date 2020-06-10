import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import { startCase } from "lodash"
import CustomFieldSetupForm from "app/WorkspaceSettings/CustomFields/CustomFieldSetupForm"
import GetCustomFields from "graphql/queries/GetCustomFields"
import CreateCustomFieldMutation from "graphql/mutations/CreateCustomField"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class CustomFieldSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      // If no `validators` key exists, we need to add it.
      if (variables && !variables.hasOwnProperty("validators")) {
        variables.validators = {}
      }

      const { contentType } = this.props
      const payload = {
        variables: { contentType, ...variables },
        successMessage: "Custom field has been created.",
        refetchQueries: [
          {
            query: GetCustomFields,
            variables: {
              contentType,
            },
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    this.props.form.resetFields()
    this.props.onCancel()
  }

  render() {
    const { form, submitting, contentType, visible, onCancel } = this.props
    return (
      <Modal
        title={`Create New ${startCase(contentType.toLowerCase())} Field`}
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <CustomFieldSetupForm
          form={form}
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
        />
      </Modal>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  graphql(CreateCustomFieldMutation),
  withGraphQLMutation
)

export default enhance(CustomFieldSetup)
