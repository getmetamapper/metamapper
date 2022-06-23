import React, { Component, Fragment } from "react"
import { graphql, compose } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter } from "react-router-dom"
import { Button, Modal, Form, Input } from "antd"
import DeleteCheckAlertRuleMutation from "graphql/mutations/DeleteCheckAlertRule"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteCheckAlertRule extends Component {
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

    const { ruleId } = this.props
    const payload = {
      successMessage: "Alert rule has been deleted.",
      variables: { id: ruleId },
      refetchQueries: ["GetCheckAlertRules"],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    this.handleCancel()
  }

  render() {
    const { deleteConfirm, visible } = this.state
    const { submitting } = this.props
    return (
      <Fragment>
        <Modal
          visible={visible}
          title="Delete this alert rule"
          onCancel={this.handleCancel}
          footer={[
            <Button
              key="submit"
              type="danger"
              disabled={deleteConfirm !== "delete me" || submitting}
              onClick={this.handleSubmit}
              data-test="DeleteCheckAlertRule.Submit"
            >
              {submitting ? 'Deleting...' : 'Delete this alert rule'}
            </Button>,
          ]}
        >
          <Form>
            <p>
              Once you delete an alert rule, you will lose all data related to it.
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
                data-test="DeleteCheckAlertRule.ConfirmationPrompt"
              />
            </Form.Item>
          </Form>
        </Modal>
        {/* eslint-disable-next-line */}
        <a role="button" onClick={() => this.setState({ visible: true })}>
          Delete
        </a>
      </Fragment>
    )
  }
}

const enhance = compose(
  withRouter,
  withUserContext,
  graphql(DeleteCheckAlertRuleMutation),
  withGraphQLMutation
)

export default enhance(DeleteCheckAlertRule)
