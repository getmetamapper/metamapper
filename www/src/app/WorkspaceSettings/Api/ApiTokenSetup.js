import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Form, Modal } from "antd"
import { withUserContext } from "context/UserContext"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import ApiTokenSetupForm from "app/WorkspaceSettings/Api/ApiTokenSetupForm"
import GetApiTokens from "graphql/queries/GetApiTokens"
import CreateApiTokenMutation from "graphql/mutations/CreateApiToken"

class ApiTokenSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Access token has been created.",
        refetchQueries: [
          {
            query: GetApiTokens,
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { apiToken, secret, errors } = data.createApiToken

    if (!errors) {
      this.props.onSuccess(apiToken.name, secret)
      this.props.form.resetFields()
    }
  }

  render() {
    const { form, submitting, visible, onCancel } = this.props
    return (
      <Modal
        title="Create Access Token"
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <ApiTokenSetupForm
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
  withRouter,
  withUserContext,
  graphql(CreateApiTokenMutation),
  withGraphQLMutation,
)

export default enhance(ApiTokenSetup)
