import React, { Component } from "react"
import { compose } from "react-apollo"
import { Divider } from "antd"
import { withSuperUserAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import WorkspaceLayout from "app/WorkspaceSettings/WorkspaceLayout"
import GroupSetup from "app/WorkspaceSettings/Groups/GroupSetup"
import WorkspaceGroupsTable from "app/WorkspaceSettings/Groups/WorkspaceGroupsTable"
import UpdateGroup from "app/WorkspaceSettings/Groups/UpdateGroup"
import DeleteGroup from "app/WorkspaceSettings/Groups/DeleteGroup"
import ManageGroupUsers from "app/WorkspaceSettings/Groups/ManageGroupUsers"
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
      label: "Groups",
      to: `/${slug}/settings/Groups`,
    },
  ]
}

class Groups extends Component {
  constructor(props) {
    super(props)

    this.state = {
      setupVisible: false,
      updateVisible: false,
      updatingGroup: null,
      deleteVisible: false,
      deletingGroup: null,
      manageVisible: false,
      managingGroup: null,
    }
  }

  onOpenSetupForm = () => {
    this.setState({ setupVisible: true })
  }

  onCloseSetupForm = () => {
    this.setState({ setupVisible: false })
  }

  onOpenUpdateForm = (updatingGroup) => {
    this.setState({ updateVisible: true, updatingGroup })
  }

  onCloseUpdateForm = () => {
    this.setState({ updateVisible: false })
  }

  onOpenDeleteForm = (deletingGroup) => {
    this.setState({ deleteVisible: true, deletingGroup })
  }

  onCloseDeleteForm = () => {
    this.setState({ deleteVisible: false })
  }

  onOpenManageForm = (managingGroup) => {
    this.setState({ manageVisible: true, managingGroup })
  }

  onCloseManageForm = () => {
    this.setState({ manageVisible: false })
  }

  render() {
    const {
      deleteVisible,
      deletingGroup,
      manageVisible,
      managingGroup,
      setupVisible,
      updateVisible,
      updatingGroup,
    } = this.state
    const {
      loading,
      hasPermission,
      workspace,
    } = this.props
    return (
      <WorkspaceLayout
        title={`Groups - ${workspace.slug} - Metamapper`}
        breadcrumbs={breadcrumbs}
      >
        <h2>Groups</h2>
        <Divider />
        <p>
          Groups are a generic way of categorizing users so you can apply permissions (or some other label) to your team members.
        </p>
        <RestrictedButton
          type="primary"
          onClick={this.onOpenSetupForm}
          hasPermission={hasPermission}
        >
          Add New Group
        </RestrictedButton>
        <>
          <WorkspaceGroupsTable
            loading={loading}
            hasPermission={hasPermission}
            onUpdate={this.onOpenUpdateForm}
            onDelete={this.onOpenDeleteForm}
            onManage={this.onOpenManageForm}
          />
        </>
        <>
          <GroupSetup
            visible={setupVisible}
            onCancel={this.onCloseSetupForm}
          />
        </>
        <>
          <UpdateGroup
            group={updatingGroup}
            visible={updateVisible}
            onCancel={this.onCloseUpdateForm}
          />
        </>
        <>
          <DeleteGroup
            group={deletingGroup}
            visible={deleteVisible}
            onCancel={this.onCloseDeleteForm}
          />
        </>
        <>
          <ManageGroupUsers
            group={managingGroup}
            visible={manageVisible}
            onCancel={this.onCloseManageForm}
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
  withSuperUserAccess,
  withLargeLoader,
  withNotFound,
)(Groups)
