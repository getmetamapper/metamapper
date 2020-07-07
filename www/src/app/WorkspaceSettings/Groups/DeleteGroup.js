import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { Button, Modal, Form, Input } from "antd"
import GetWorkspaceGroups from "graphql/queries/GetWorkspaceGroups"
import DeleteGroupMutation from "graphql/mutations/DeleteGroup"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteGroup extends Component {
  state = {
    deleteConfirm: "",
  }

  handleCancel = () => {
    this.setState({ deleteConfirm: "" })
    this.props.onCancel()
  }

  changeDeleteConfirm = (evt) => {
    this.setState({
      deleteConfirm: evt.target.value,
    })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const {
      group: { id },
    } = this.props
    const payload = {
      successMessage: "Group has been removed.",
      variables: { id },
      refetchQueries: [
        {
          query: GetWorkspaceGroups,
        },
      ],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    this.handleCancel()
  }

  render() {
    const { deleteConfirm } = this.state
    const { submitting, visible } = this.props
    return (
      <Modal
        visible={visible}
        title="Delete this group"
        onCancel={this.handleCancel}
        footer={[
          <Button
            key="submit"
            type="danger"
            disabled={deleteConfirm !== "delete me" || submitting}
            onClick={this.handleSubmit}
            data-test="DeleteGroup.Submit"
          >
            {submitting ? 'Deleting...' : 'Delete this group'}
          </Button>,
        ]}
      >
        <Form>
          <p>
            Once you delete a group, you will lose all data related to it.
          </p>
          <p>
            To continue with deletion, please type <b>delete me</b> in the box
            below.
          </p>
          <Form.Item>
            <Input
              type="text"
              placeholder="delete me"
              onChange={this.changeDeleteConfirm}
              value={this.state.deleteConfirm}
              data-test="DeleteGroup.ConfirmationPrompt"
            />
          </Form.Item>
        </Form>
      </Modal>
    )
  }
}

const enhance = compose(
  withRouter,
  withUserContext,
  graphql(DeleteGroupMutation),
  withGraphQLMutation
)

export default enhance(DeleteGroup)
