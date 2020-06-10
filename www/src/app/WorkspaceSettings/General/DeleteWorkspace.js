import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { withOwnersOnly } from "hoc/withPermissionsRequired"
import { Button, Modal, Form, Input } from "antd"
import RestrictedButton from "app/Common/RestrictedButton"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteWorkspaceMutation from "graphql/mutations/DeleteWorkspace"

class DeleteWorkspace extends Component {
  state = {
    visible: false,
    deleteConfirm: "",
  }

  showModal = () => {
    this.setState({
      deleteConfirm: "",
      visible: true,
    })
  }

  handleCancel = () => {
    this.setState({
      deleteConfirm: "",
      visible: false,
    })
  }

  changeDeleteConfirm = (evt) => {
    this.setState({
      deleteConfirm: evt.target.value,
    })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      workspace: { id },
    } = this.props
    const payload = {
      successMessage: "Workspace has been deleted.",
      variables: { id },
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
    this.handleCancel()
  }

  handleSubmitSuccess = ({ data }) => {
    const { ok, errors } = data.deleteWorkspace

    if (ok && !errors) {
      this.props.refreshUser()
      this.props.history.push(`/workspaces`)
    }
  }

  render() {
    const { deleteConfirm, visible } = this.state
    const { hasPermission } = this.props
    return (
      <>
        <RestrictedButton
          type="danger"
          htmlType="submit"
          onClick={this.showModal}
          hasPermission={hasPermission}
          data-test="DeleteWorkspace.Open"
        >
          Delete This Workspace
        </RestrictedButton>
        <Modal
          visible={visible && hasPermission}
          title="Delete this workspace"
          onCancel={this.handleCancel}
          footer={[
            <Button
              key="submit"
              type="danger"
              disabled={deleteConfirm !== "delete me"}
              onClick={this.handleSubmit}
              data-test="DeleteWorkspace.Submit"
            >
              Delete this workspace
            </Button>,
          ]}
        >
          <Form>
            <p>
              Once you delete a workspace, you will lose all data related to it.
              Please be sure that this is what you want to do, as there is no
              going back!
            </p>
            <p>
              To continue with deleting this workspace, please type{" "}
              <b>delete me</b> in the box below.
            </p>
            <Form.Item>
              <Input
                type="text"
                placeholder="delete me"
                onChange={this.changeDeleteConfirm}
                value={this.state.deleteConfirm}
                data-test="DeleteWorkspace.ConfirmationPrompt"
              />
            </Form.Item>
          </Form>
        </Modal>
      </>
    )
  }
}

const enhance = compose(
  withRouter,
  withUserContext,
  withOwnersOnly,
  graphql(DeleteWorkspaceMutation),
  withGraphQLMutation
)

export default enhance(DeleteWorkspace)
