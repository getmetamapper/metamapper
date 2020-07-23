import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { Button, Modal, Form, Input } from "antd"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DeleteDatastoreMutation from "graphql/mutations/DeleteDatastore"

class DeleteDatastore extends Component {
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
      datastore: { id },
    } = this.props
    const payload = {
      successMessage: "Datastore has been removed.",
      variables: { id },
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
    this.handleCancel()
  }

  handleSubmitSuccess = ({ data }) => {
    const { ok, errors } = data.deleteDatastore
    const {
      currentWorkspace: { slug: workspaceSlug },
    } = this.props

    if (ok && !errors) {
      this.props.history.push(`/${workspaceSlug}/datastores`)
    }
  }

  render() {
    const { deleteConfirm, visible } = this.state
    const { submitting } = this.props
    return (
      <>
        <span className="link" onClick={this.showModal} data-test="DeleteDatastore.Open">
          Delete This Datastore
        </span>
        <Modal
          visible={visible}
          title="Delete this datastore"
          onCancel={this.handleCancel}
          footer={[
            <Button
              key="submit"
              type="danger"
              disabled={deleteConfirm !== "delete me" || submitting}
              onClick={this.handleSubmit}
              data-test="DeleteDatastore.Submit"
            >
              {submitting ? 'Processing...' : 'Delete this datastore'}
            </Button>,
          ]}
        >
          <Form>
            <p>
              Once you delete a datastore, you will lose all data related to it.
              Therefore, before you delete your datastore, make sure you have
              backed up any data that you might need.
            </p>
            <p>
              This action will only delete the datastore in Metamapper. No data
              will be deleted from your database.
            </p>
            <p>
              To continue with deleting this datastore, please type{" "}
              <b>delete me</b> in the box below.
            </p>
            <Form.Item>
              <Input
                type="text"
                placeholder="delete me"
                onChange={this.changeDeleteConfirm}
                value={this.state.deleteConfirm}
                data-test="DeleteDatastore.ConfirmationPrompt"
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
  graphql(DeleteDatastoreMutation),
  withGraphQLMutation
)

export default enhance(DeleteDatastore)
