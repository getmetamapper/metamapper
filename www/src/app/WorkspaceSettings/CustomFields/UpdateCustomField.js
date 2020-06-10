import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import { startCase } from "lodash"
import UpdateCustomFieldForm from "app/WorkspaceSettings/CustomFields/UpdateCustomFieldForm"
import GetCustomFields from "graphql/queries/GetCustomFields"
import UpdateCustomFieldMutation from "graphql/mutations/UpdateCustomField"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateCustomField extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        customField: { id },
        contentType,
      } = this.props

      const payload = {
        variables: { id, ...variables },
        successMessage: "Custom field has been updated.",
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
    const {
      form,
      customField,
      submitting,
      contentType,
      visible,
      onCancel,
    } = this.props
    return (
      <Modal
        title={`Update ${startCase(contentType.toLowerCase())} Field`}
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <UpdateCustomFieldForm
          customField={customField}
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
  graphql(UpdateCustomFieldMutation),
  withGraphQLMutation
)

export default enhance(UpdateCustomField)
