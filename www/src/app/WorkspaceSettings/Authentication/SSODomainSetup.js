import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import CreateSSODomainMutation from "graphql/mutations/CreateSSODomain"
import GetSSODomains from "graphql/queries/GetSSODomains"
import SSODomainSetupForm from "./SSODomainSetupForm"

class SSODomainSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Domain has been added and is pending verification.",
        refetchQueries: [
          {
            query: GetSSODomains,
            variables: {},
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.createSSODomain

    if (!errors) {
      this.props.form.resetFields()
    }
  }

  render() {
    const { form, hasPermission, submitting } = this.props
    return (
      <SSODomainSetupForm
        form={form}
        hasPermission={hasPermission}
        isSubmitting={submitting}
        onSubmit={this.handleSubmit}
      />
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withSuperUserAccess,
  withForm,
  graphql(CreateSSODomainMutation),
  withGraphQLMutation
)

export default enhance(SSODomainSetup)
