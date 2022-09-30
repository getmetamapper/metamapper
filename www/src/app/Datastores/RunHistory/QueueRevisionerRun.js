import React, { Component, Fragment } from "react"
import { graphql, compose } from "react-apollo"
import { Alert } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import RestrictedButton from "app/Common/RestrictedButton"
import QueueRevisionerRunMutation from "graphql/mutations/QueueRevisionerRun"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class QueueRevisionerRun extends Component {
  handleSubmit = (evt) => {
    evt.preventDefault()

    const { datastore } = this.props

    const payload = {
      variables: {
        datastoreId: datastore.id,
      },
      successMessage: "Resync request was submitted.",
      refetchQueries: [
        "GetDatastoreRunHistory",
      ],
    }

    this.props.handleMutation(payload)
  }

  render() {
    const { hasPermission, submitting } = this.props
    if (!hasPermission) return null
    return (
      <div className="queue-revisioner-run">
        <Alert
          description={
            <Fragment>
              <p>
                As a workspace owner, you can trigger a datastore resync
                manually by clicking the button below.
              </p>
              <RestrictedButton
                type="default"
                hasPermission={hasPermission}
                isSubmitting={submitting}
                onClick={this.handleSubmit}
                data-test="QueueRevisionerRun.Submit"
              >
                {submitting ? "Submitting..." : "Resync Datastore"}
              </RestrictedButton>
            </Fragment>
          }
        />
      </div>
    )
  }
}

export default compose(
  graphql(QueueRevisionerRunMutation),
  withGraphQLMutation,
  withSuperUserAccess,
)(QueueRevisionerRun)
