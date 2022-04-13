import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Form } from "antd"
import { map, differenceWith, isEqual } from "lodash"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import AllowedCustomPropertySettingsForm from "app/Datastores/DatastoreSettings/AllowedCustomPropertySettingsForm"
import DisableDatastoreCustomFieldsMutation from "graphql/mutations/DisableDatastoreCustomFields"
import withGetCustomDatastoreFields from "graphql/withGetCustomDatastoreFields"
import withGetCustomTableFields from "graphql/withGetCustomTableFields"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class AllowedCustomPropertySettings extends Component {
  constructor(props) {
    super(props);

    this.state = {
      availableDatastoreProperties: map(props.customDatastoreFields, "pk"),
      availableTableProperties: map(props.customTableFields, "pk"),
      labelizedDatastoreProperties: this.labelize(props.customDatastoreFields),
      labelizedTableProperties: this.labelize(props.customTableFields),
    }
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { id } = this.props.datastore

    const {
      availableDatastoreProperties,
      availableTableProperties
    } = this.state

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        enabledDatastoreProperties,
        enabledTableProperties,
      } = variables

      const disabledDatastoreProperties = this.differenceWith(
        availableDatastoreProperties,
        enabledDatastoreProperties,
      )

      const disabledTableProperties = this.differenceWith(
        availableTableProperties,
        enabledTableProperties,
      )

      const payload = {
        variables: {
          id,
          disabledTableProperties,
          disabledDatastoreProperties,
        },
        successMessage: "Allowed custom properties has been updated for this datastore.",
      }

      this.props.handleMutation(payload)
    })
  }

  labelize = (fields) => {
    return map(fields, ({ pk, fieldName }) => ({ value: pk, label: fieldName }))
  }

  differenceWith = (a, b) => {
    return differenceWith(a, b, isEqual)
  }

  render() {
    const {
      datastore,
      form,
      hasPermission,
      submitting,
      customDatastoreFields,
      customTableFields,
    } = this.props

    const {
      availableDatastoreProperties,
      availableTableProperties,
    } = this.state

    const enabledDatastoreProperties = this.differenceWith(
      availableDatastoreProperties,
      datastore.disabledDatastoreProperties,
    )

    const enabledTableProperties = this.differenceWith(
      availableTableProperties,
      datastore.disabledTableProperties,
    )

    return (
      <AllowedCustomPropertySettingsForm
        datastore={datastore}
        form={form}
        customDatastoreFields={customDatastoreFields}
        enabledDatastoreProperties={enabledDatastoreProperties}
        customTableFields={customTableFields}
        enabledTableProperties={enabledTableProperties}
        hasPermission={hasPermission}
        isSubmitting={submitting}
        onSubmit={this.handleSubmit}
      />
    )
  }
}

const withForm = Form.create()

const enhance = compose(
  withForm,
  withWriteAccess,
  withGetCustomDatastoreFields,
  withGetCustomTableFields,
  withLargeLoader,
  graphql(DisableDatastoreCustomFieldsMutation),
  withGraphQLMutation,
)

export default enhance(AllowedCustomPropertySettings)
