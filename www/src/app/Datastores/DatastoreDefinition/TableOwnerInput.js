import React, { Component } from "react"
import { Tag, Tooltip } from "antd"
import { capitalize } from "lib/utilities"
import GroupAvatar from "app/Common/GroupAvatar"
import UserAvatar from "app/Common/UserAvatar"
import Link from "app/Navigation/Link"
import DeleteAssetOwner from "app/Datastores/DatastoreDefinition/DeleteAssetOwner"

const TableOwnerGroupDisplay = ({ ownerId, classification, owner: { id, pk, name }, isEditing }) => (
  <div className="table-owner-display" data-test={`TableOwner.Item(${ownerId})`}>
    <GroupAvatar pk={pk} name={name} />
    <div className="metadata">
      <div className="name">
        <Link to={`/settings/groups/${id}`}>{name}</Link>
      </div>
    </div>
    <div className="icon">
      <Tooltip title="Owner Classification"><Tag>{capitalize(classification.toLowerCase())}</Tag></Tooltip>
      {isEditing && (
        <DeleteAssetOwner ownerId={ownerId} refetchQueries={['GetTableDefinitionWithOwners']} />
      )}
    </div>
  </div>
)

const TableOwnerUserDisplay = ({ ownerId, classification, owner: { id, pk, name, avatarUrl }, isEditing }) => (
  <div className="table-owner-display" data-test={`TableOwner.Item(${ownerId})`}>
    <UserAvatar pk={pk} name={name} email={name} avatarUrl={avatarUrl} />
    <div className="metadata">
      <div className="name">
        <Link to={`/settings/users/${id}`}>{name}</Link>
      </div>
    </div>
    <div className="icon">
      <Tooltip title="Owner Classification"><Tag>{capitalize(classification.toLowerCase())}</Tag></Tooltip>
      {isEditing && (
        <DeleteAssetOwner ownerId={ownerId} refetchQueries={['GetTableDefinitionWithOwners']} />
      )}
    </div>
  </div>
)

const displayMapping = {
  GROUP: TableOwnerGroupDisplay,
  USER: TableOwnerUserDisplay,
}

class TableOwnerDisplay extends Component {
  render () {
    const { type, ...restProps } = this.props
    const Component = displayMapping[type]

    return <Component {...restProps} />
  }
}

export default TableOwnerDisplay
