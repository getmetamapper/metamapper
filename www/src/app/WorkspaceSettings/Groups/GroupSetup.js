import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import GroupSetupForm from "app/WorkspaceSettings/Groups/GroupSetupForm"
import GetWorkspaceGroups from "graphql/queries/GetWorkspaceGroups"
import CreateGroupMutation from "graphql/mutations/CreateGroup"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class GroupSetup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables,
        successMessage: "Group has been created.",
        refetchQueries: [
          {
            query: GetWorkspaceGroups,
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.createGroup

    if (!errors || errors.length <= 0) {
      this.props.form.resetFields()
      this.props.onCancel()
    }
  }

  render() {
    const { form, submitting, visible, onCancel } = this.props
    return (
      <Modal
        title="Create New Group"
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <GroupSetupForm
          form={form}
          onSubmit={this.handleSubmit}
          isSubmitting={submitting}
        />
      </Modal>
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  graphql(CreateGroupMutation),
  withGraphQLMutation
)

export default enhance(GroupSetup)
