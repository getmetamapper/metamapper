import React from "react"
import { Helmet } from "react-helmet"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import UpdatePasswordForm from "app/UserSettings/Security/UpdatePasswordForm"
import UpdateUserPasswordMutation from "graphql/mutations/UpdateUserPassword"

class UpdatePassword extends React.Component {
  state = {
    submitting: false,
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Your password has been changed.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.updateCurrentUser

    if (!errors) {
      this.props.form.resetFields()
    }
  }

  render() {
    const { form, submitting } = this.props
    return (
      <>
        <Helmet>
          <script
            type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/zxcvbn/4.4.2/zxcvbn.js"
            secure
          />
        </Helmet>
        <UpdatePasswordForm
          form={form}
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
        />
      </>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  graphql(UpdateUserPasswordMutation),
  withGraphQLMutation
)

export default enhance(UpdatePassword)
