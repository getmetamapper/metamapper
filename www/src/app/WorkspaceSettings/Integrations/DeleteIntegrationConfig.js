import React, { Component, Fragment } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { Button, Modal, Form, Input } from "antd"
import DeleteIntegrationConfigMutation from "graphql/mutations/DeleteIntegrationConfig"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteIntegrationConfig extends Component {
  state = {
    deleteConfirm: "",
    visible: false,
  }

  handleCancel = () => {
    this.setState({ deleteConfirm: "", visible: false })
  }

  changeDeleteConfirm = (evt) => {
    this.setState({
      deleteConfirm: evt.target.value,
    })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { integrationConfig } = this.props
    const payload = {
      successMessage: "Integration has been removed.",
      variables: { id: integrationConfig.id },
      refetchQueries: ["GetIntegrationConfigs"],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    this.handleCancel()
  }

  render() {
    const { deleteConfirm, visible } = this.state
    const { hasPermission, submitting } = this.props
    return (
      <Fragment>
        <Modal
          visible={visible}
          title="Delete this integration"
          onCancel={this.handleCancel}
          footer={[
            <Button
              key="submit"
              type="danger"
              disabled={deleteConfirm !== "delete me" || submitting}
              onClick={this.handleSubmit}
              data-test="DeleteIntegrationConfig.Submit"
            >
              {submitting ? 'Deleting...' : 'Delete this integration'}
            </Button>,
          ]}
        >
          <Form>
            <p>
              Once you delete a integration, you will lose all data related to it.
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
                data-test="DeleteIntegrationConfig.ConfirmationPrompt"
              />
            </Form.Item>
          </Form>
        </Modal>
        <Button
          type="default"
          shape="circle"
          icon="delete"
          size="small"
          disabled={!hasPermission}
          onClick={() => this.setState({ visible: true })}
        />
      </Fragment>
    )
  }
}

const enhance = compose(
  withRouter,
  withUserContext,
  graphql(DeleteIntegrationConfigMutation),
  withGraphQLMutation
)

export default enhance(DeleteIntegrationConfig)
