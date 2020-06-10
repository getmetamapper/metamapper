import React from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { withUserContext } from "context/UserContext"
import { setToken } from "lib/utilities"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import UpdateUserProfileForm from "app/UserSettings/Profile/UpdateUserProfileForm"
import UpdateUserProfileMutation from "graphql/mutations/UpdateUserProfile"

class UpdatePassword extends React.Component {
  state = {
    submitting: false,
  }

  setToken = setToken

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Your profile has been updated.",
      }

      this.props.handleMutation(payload, this.handleSuccess)
    })
  }

  handleSuccess = ({ data: { updateCurrentUser } }) => {
    const { jwt, errors } = updateCurrentUser

    if (!errors) {
      this.setToken(jwt)
      this.props.refreshUser()
    }
  }

  render() {
    const { form, user, submitting } = this.props
    return (
      <UpdateUserProfileForm
        form={form}
        user={user}
        onSubmit={this.handleSubmit}
        isSubmitting={submitting}
      />
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withUserContext,
  graphql(UpdateUserProfileMutation),
  withGraphQLMutation
)

export default enhance(UpdatePassword)
