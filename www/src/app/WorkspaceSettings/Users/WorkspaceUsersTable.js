import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Table } from "antd"
import { PERMISSION_CHOICES } from "lib/constants"
import { coalesce } from "lib/utilities"
import { filter } from "lodash"
import withLoader from "hoc/withLoader"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withPermissionsRequired from "hoc/withPermissionsRequired"
import GetWorkspaceUsers from "graphql/queries/GetWorkspaceUsers"
import GrantMembershipMutation from "graphql/mutations/GrantMembership"
import RevokeMembershipMutation from "graphql/mutations/RevokeMembership"
import DisplayUsername from "./DisplayUsername"
import UpdateUserPermission from "./UpdateUserPermission"
import RemoveUserPermission from "./RemoveUserPermission"

class WorkspaceUsersTable extends Component {
  constructor(props) {
    super(props)

    const ownersCount = filter(props.workspaceUsers, { permissions: "OWNER" })
      .length

    this.columns = [
      {
        title: "Name",
        sorter: (a, b) => coalesce(b.name, b.email).charCodeAt(0),
        render: (record) => <DisplayUsername {...record} />,
      },
      {
        title: "Role",
        dataIndex: "permissions",
        filters: Object.keys(PERMISSION_CHOICES).map((key) => ({
          text: PERMISSION_CHOICES[key],
          value: key,
        })),
        onFilter: (value, record) => value === record.permissions,
        render: (permissions, record) => (
          <UpdateUserPermission
            workspace={props.workspace}
            hasPermission={props.hasPermission}
            {...record}
          />
        ),
      },
      {
        align: "right",
        render: (record) => (
          <RemoveUserPermission
            workspace={props.workspace}
            hasPermission={props.hasPermission}
            isLastOwner={record.permissions === "OWNER" && ownersCount <= 1}
            {...record}
          />
        ),
      },
    ]
  }

  handleRevokeMembership = (membership) => {
    const { workspace } = this.props
    const payload = {
      successMessage: "Membership has been revoked.",
      variables: {
        email: membership.email,
      },
      refetchQueries: [
        {
          query: GetWorkspaceUsers,
          variables: {
            workspaceId: workspace.id,
            activeOnly: false,
          },
        },
      ],
    }

    this.props.handleMutation(payload, null, "revokeMembership")
  }

  render() {
    const { workspaceUsers } = this.props
    return (
      <span data-test="WorkspaceUsersTable">
        <Table
          rowKey="email"
          dataSource={workspaceUsers}
          columns={this.columns}
        />
      </span>
    )
  }
}

const withSpinLoader = withLoader({
  size: "small",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

const withGrantGraphQL = graphql(GrantMembershipMutation, {
  name: "grantMembership",
})

const withRevokeGraphQL = graphql(RevokeMembershipMutation, {
  name: "revokeMembership",
})

const withOwnersOnly = withPermissionsRequired({
  roles: ["OWNER"],
})

const enhance = compose(
  withSpinLoader,
  withOwnersOnly,
  withGrantGraphQL,
  withRevokeGraphQL,
  withGraphQLMutation
)

export default enhance(WorkspaceUsersTable)
