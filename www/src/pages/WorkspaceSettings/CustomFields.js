import React, { Component } from "react"
import { compose } from "react-apollo"
import { Divider, Tabs } from "antd"
import { map } from "lodash"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import CustomFieldSetup from "app/WorkspaceSettings/CustomFields/CustomFieldSetup"
import CustomFieldsTable from "app/WorkspaceSettings/CustomFields/CustomFieldsTable"
import UpdateCustomField from "app/WorkspaceSettings/CustomFields/UpdateCustomField"
import DeleteCustomField from "app/WorkspaceSettings/CustomFields/DeleteCustomField"
import RestrictedButton from "app/Common/RestrictedButton"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"

const breadcrumbs = ({ slug }) => {
  return [
    {
      label: "Home",
      to: `/${slug}/datastores`,
    },
    {
      label: "Workspace Settings",
      to: `/${slug}/settings`,
    },
    {
      label: "Custom Fields",
      to: `/${slug}/settings/customfields`,
    },
  ]
}

class CustomFields extends Component {
  constructor(props) {
    super(props)

    this.state = {
      setupVisible: false,
      updateVisible: false,
      updatingField: null,
      deleteVisible: false,
      deletingField: null,
      activeKey: "DATASTORE",
      tabs: [
        {
          pluralized: "Datastores",
          singularized: "Datastore",
          key: "DATASTORE",
        },
        {
          pluralized: "Tables",
          singularized: "Table",
          key: "TABLE",
        },
      ],
    }
  }

  onOpenSetupForm = () => {
    this.setState({ setupVisible: true })
  }

  onCloseSetupForm = () => {
    this.setState({ setupVisible: false })
  }

  onOpenUpdateForm = (updatingField) => {
    this.setState({ updateVisible: true, updatingField })
  }

  onCloseUpdateForm = () => {
    this.setState({ updateVisible: false })
  }

  onOpenDeleteForm = (deletingField) => {
    this.setState({ deleteVisible: true, deletingField })
  }

  onCloseDeleteForm = () => {
    this.setState({ deleteVisible: false })
  }

  onChange = (activeKey) => {
    this.setState({ activeKey })
  }

  render() {
    const {
      activeKey,
      updatingField,
      updateVisible,
      deletingField,
      deleteVisible,
      setupVisible,
    } = this.state
    const { loading, hasPermission, workspace } = this.props
    return (
      <WorkspaceLayout
        title={`Custom Fields - ${workspace.slug} - Metamapper`}
        breadcrumbs={breadcrumbs}
      >
        <h2>Custom Fields</h2>
        <Divider />
        <p>
          You can use custom fields to document more specific information about
          your data assets, such as product area, data steward, ETL source, etc.
        </p>
        <Tabs type="card" activeKey={activeKey} onChange={this.onChange}>
          {map(this.state.tabs, ({ singularized, pluralized, key }) => (
            <Tabs.TabPane tab={pluralized} key={key}>
              <RestrictedButton
                type="primary"
                onClick={this.onOpenSetupForm}
                hasPermission={hasPermission}
              >
                Add Custom {singularized} Field
              </RestrictedButton>
            </Tabs.TabPane>
          ))}
        </Tabs>
        <>
          <CustomFieldsTable
            loading={loading}
            contentType={activeKey}
            hasPermission={hasPermission}
            onUpdate={this.onOpenUpdateForm}
            onDelete={this.onOpenDeleteForm}
          />
        </>
        <>
          <CustomFieldSetup
            visible={setupVisible}
            contentType={activeKey}
            onCancel={this.onCloseSetupForm}
          />
        </>
        <>
          <UpdateCustomField
            customField={updatingField}
            visible={updateVisible}
            contentType={activeKey}
            onCancel={this.onCloseUpdateForm}
          />
        </>
        <>
          <DeleteCustomField
            customField={deletingField}
            visible={deleteVisible}
            contentType={activeKey}
            onCancel={this.onCloseDeleteForm}
          />
        </>
      </WorkspaceLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ workspace }) => {
  return !workspace || !workspace.hasOwnProperty("id")
})

export default compose(
  withGetWorkspaceBySlug,
  withWriteAccess,
  withLargeLoader,
  withNotFound,
)(CustomFields)
