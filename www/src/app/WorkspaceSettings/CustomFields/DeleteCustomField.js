import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { Button, Modal, Form, Input } from "antd"
import GetCustomFields from "graphql/queries/GetCustomFields"
import DeleteCustomFieldMutation from "graphql/mutations/DeleteCustomField"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteCustomField extends Component {
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
      customField: { id },
      contentType,
    } = this.props
    const payload = {
      successMessage: "Custom property has been removed.",
      variables: { id },
      refetchQueries: [
        {
          query: GetCustomFields,
          variables: {
            contentType,
          },
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
        title="Delete this custom property"
        onCancel={this.handleCancel}
        footer={[
          <Button
            key="submit"
            type="danger"
            disabled={deleteConfirm !== "delete me" || submitting}
            onClick={this.handleSubmit}
            data-test="DeleteCustomField.Submit"
          >
            {submitting ? 'Deleting...' : 'Delete this custom property'}
          </Button>,
        ]}
      >
        <Form>
          <p>
            Once you delete a custom property, you will lose all data related to
            it.
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
              data-test="DeleteCustomField.ConfirmationPrompt"
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
  graphql(DeleteCustomFieldMutation),
  withGraphQLMutation
)

export default enhance(DeleteCustomField)
