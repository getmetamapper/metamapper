import React, { Component } from "react"
import { compose } from "react-apollo"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import DatastoreNotificationSettingsForm from "app/Datastores/DatastoreSettings/DatastoreNotificationSettingsForm"

class DatastoreNotificationSettings extends Component {
  constructor(props) {
    super(props);
  }

  handleSubmit = (evt) => {

  }

  render() {
    const { notificationSettings, submitting } = this.props

    return (
      <DatastoreNotificationSettingsForm
        notificationSettings={notificationSettings}
        isSubmitting={submitting}
        onSubmit={this.handleSubmit}
      />
    )
  }
}

const enhance = compose(
  withWriteAccess,
  withLargeLoader,
  withGraphQLMutation,
)

export default enhance(DatastoreNotificationSettings)
