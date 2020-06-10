import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Form } from "antd"
import withLoader from "hoc/withLoader"
import { withOwnersOnly } from "hoc/withPermissionsRequired"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import UpdateWorkspaceMutation from "graphql/mutations/UpdateWorkspace"
import UpdateWorkspaceForm from "./UpdateWorkspaceForm"

class UpdateWorkspace extends Component {
  state = { avatar: null }

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Workspace has been updated.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { workspace, errors } = data.updateWorkspace
    const {
      match: {
        params: { workspaceSlug },
      },
    } = this.props

    if (workspace && !errors) {
      const { history } = this.props

      if (workspace.slug !== workspaceSlug) {
        history.push(`/${workspace.slug}/settings`)
      }
    }
  }

  render() {
    const { form, hasPermission, workspace, submitting } = this.props
    return (
      <>
        <UpdateWorkspaceForm
          workspace={workspace}
          form={form}
          hasPermission={hasPermission}
          isSubmitting={submitting}
          onSubmit={this.handleSubmit}
        />
      </>
    )
  }
}

const withSpinLoader = withLoader({
  size: "small",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

const withForm = Form.create()

const enhance = compose(
  withSpinLoader,
  withRouter,
  withOwnersOnly,
  withForm,
  graphql(UpdateWorkspaceMutation),
  withGraphQLMutation
)

export default enhance(UpdateWorkspace)
