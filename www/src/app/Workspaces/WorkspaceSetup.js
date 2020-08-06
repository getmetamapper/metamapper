import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Form, Modal } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { withUserContext } from "context/UserContext"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetBeaconActivatedStatus from "graphql/withGetBeaconActivatedStatus"
import WorkspaceSetupForm from "app/Workspaces/WorkspaceSetupForm"
import CreateWorkspaceMutation from "graphql/mutations/CreateWorkspace"

class WorkspaceSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Workspace has been created.",
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { workspace, errors } = data.createWorkspace

    if (!errors && workspace && workspace.hasOwnProperty("slug")) {
      this.props.config.setCurrentWorkspace(workspace)
      this.props.refreshUser()

      window.location.href = `/${workspace.slug}/datastores/new`
    }
  }

  render() {
    const { beaconActivated, form, submitting, visible, onCancel } = this.props
    return (
      <Modal
        title="Create New Workspace"
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <WorkspaceSetupForm
          form={form}
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
          hasBeaconActivated={beaconActivated}
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
  withGetBeaconActivatedStatus,
  withLargeLoader,
  graphql(CreateWorkspaceMutation),
  withGraphQLMutation
)

export default enhance(WorkspaceSetup)
