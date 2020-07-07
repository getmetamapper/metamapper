import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Form, Modal } from "antd"
import UpdateGroupForm from "app/WorkspaceSettings/Groups/UpdateGroupForm"
import GetWorkspaceGroups from "graphql/queries/GetWorkspaceGroups"
import UpdateGroupMutation from "graphql/mutations/UpdateGroup"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateGroup extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        group: { id },
      } = this.props

      const payload = {
        variables: { id, ...variables },
        successMessage: "Group has been updated.",
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
    const { errors } = data.updateGroup

    if (!errors || errors.length <= 0 ) {
      this.props.form.resetFields()
      this.props.onCancel()
    }
  }

  render() {
    const {
      form,
      group,
      submitting,
      visible,
      onCancel,
    } = this.props
    return (
      <Modal
        title="Update Group"
        visible={visible}
        onCancel={onCancel}
        footer={null}
      >
        <UpdateGroupForm
          group={group}
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
  graphql(UpdateGroupMutation),
  withGraphQLMutation
)

export default enhance(UpdateGroup)
