import React, { Component, Fragment } from "react"
import { graphql, compose } from "react-apollo"
import { Button, Form, Modal } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import DeleteCheck from "app/Datastores/DatastoreChecks/DeleteCheck"
import UpdateCheckForm from "app/Datastores/DatastoreChecks/UpdateCheckForm"
import UpdateCheckMutation from "graphql/mutations/UpdateCheck"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withGetCheckIntervalOptions from "graphql/withGetCheckIntervalOptions"

class UpdateCheck extends Component {
  constructor(props) {
    super(props);

    this.state = {
      visible: false
    }
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { id } = this.props.check

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const payload = {
        variables: { id, ...variables },
        successMessage: "Check has been updated.",
        refetchQueries: [
          "GetDatastoreCheck"
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { check, errors } = data.updateCheck

    if (!check || (errors && errors.length > 0)) {
      this.setState({ visible: false })
    }
  }

  render() {
    const {
      check,
      checkIntervalOptions,
      form,
      submitting,
      hasPermission,
    } = this.props
    const { visible } = this.state
    return (
      <Fragment>
        <Button icon="setting" onClick={() => this.setState({ visible: true })}>
          Settings
        </Button>
        <Modal
          title="Update Check"
          visible={visible}
          onCancel={() => this.setState({ visible: false })}
          footer={<DeleteCheck check={check} />}
        >
          <UpdateCheckForm
            form={form}
            check={check}
            checkIntervalOptions={checkIntervalOptions}
            onSubmit={this.handleSubmit}
            isSubmitting={submitting}
            hasPermission={hasPermission}
          />
        </Modal>
      </Fragment>
    )
  }
}

const enhance = compose(
  Form.create(),
  withWriteAccess,
  withGetCheckIntervalOptions,
  graphql(UpdateCheckMutation),
  withGraphQLMutation,
)

export default enhance(UpdateCheck)
