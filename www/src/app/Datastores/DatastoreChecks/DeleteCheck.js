import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { Button, Modal, Form, Input } from "antd"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteCheckMutation from "graphql/mutations/DeleteCheck"

class DeleteCheck extends Component {
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

    const { check: { id } } = this.props
    const payload = {
      successMessage: null,
      variables: { id },
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
    this.handleCancel()
  }

  handleSubmitSuccess = ({ data }) => {
    const { ok, errors } = data.deleteCheck
    const {
      currentWorkspace: { slug: workspaceSlug },
      match: {
        params: { datastoreSlug }
      },
    } = this.props

    if (ok && !errors) {
      this.props.history.push(`/${workspaceSlug}/datastores/${datastoreSlug}/checks`)
    }
  }

  render() {
    const { deleteConfirm, visible } = this.state
    const { hasPermission } = this.props
    return (
      <>
        <span className="link" onClick={this.showModal} data-test="DeleteCheck.Open">
          delete this check
        </span>
        <Modal
          visible={visible && hasPermission}
          title="Delete this check"
          onCancel={this.handleCancel}
          footer={[
            <Button
              key="submit"
              type="danger"
              disabled={deleteConfirm !== "delete me"}
              onClick={this.handleSubmit}
              data-test="DeleteCheck.Submit"
            >
              Delete this check
            </Button>,
          ]}
        >
          <Form>
            <p>
              Once you delete a check, you will lose all data related to it.
              Please be sure that this is what you want to do, as there is no
              going back!
            </p>
            <p>
              To continue with deleting this check, please type{" "}
              <b>delete me</b> in the box below.
            </p>
            <Form.Item>
              <Input
                type="text"
                placeholder="delete me"
                onChange={this.changeDeleteConfirm}
                value={this.state.deleteConfirm}
                data-test="DeleteCheck.ConfirmationPrompt"
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
  withWriteAccess,
  graphql(DeleteCheckMutation),
  withGraphQLMutation
)

export default enhance(DeleteCheck)
