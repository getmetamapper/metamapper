import React from "react"
import { List } from "antd"
import Link from "app/Navigation/Link"
import moment from "moment"
import UserAvatar from "app/Common/UserAvatar"

const ColumnActivity = ({
  datastore: { slug: datastoreSlug },
  actor,
  verb,
  target: {
    pk,
    objectType,
    displayName,
    parentResource: {
      displayName: tableName,
      parentResource: { displayName: schemaName },
    },
  },
}) => {
  let to = `/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}/columns`

  if (objectType === "Column") {
    to = `${to}?selectedColumn=${pk}`
  }

  return (
    <>
      <Link to={`/settings/users/${actor.id}`}>{actor.name}</Link> {verb} the{" "}
      <em>
        {schemaName}.{tableName}.
      </em>
      <b>
        <Link to={to}>{displayName}</Link>
      </b>{" "}
      column.
    </>
  )
}

const DatastoreActivity = ({
  datastore: { slug: datastoreSlug },
  actor,
  verb,
  target,
}) => {
  const makeLink = (text) => (
    <Link to={`/datastores/${datastoreSlug}/`}>{text}</Link>
  )
  return (
    <>
      <Link to={`/settings/users/${actor.id}`}>{actor.name}</Link> {verb} the <b>{makeLink(target.displayName)}</b>{" "}
      datastore.
    </>
  )
}

const TableActivity = ({
  datastore: { slug: datastoreSlug },
  actor,
  verb,
  target: { displayName, parentResource: parent },
}) => {
  const makeLink = (text) => (
    <Link
      to={`/datastores/${datastoreSlug}/definition/${parent.displayName}/${displayName}/overview`}
    >
      {text}
    </Link>
  )
  return (
    <>
      <Link to={`/settings/users/${actor.id}`}>{actor.name}</Link> {verb} the <em>{parent.displayName}.</em>
      <b>{makeLink(displayName)}</b> table.
    </>
  )
}

const activityMapping = {
  Column: ColumnActivity,
  Datastore: DatastoreActivity,
  Table: TableActivity,
}

const DatastoreActivityItem = ({
  actor,
  datastore,
  target,
  timestamp,
  verb,
  oldValues,
  newValues,
}) => {
  const TitleComponent = activityMapping[target.objectType]
  return (
    <List.Item className="datastore-activity-item">
      <List.Item.Meta
        avatar={<UserAvatar {...actor} />}
        title={
          <TitleComponent
            actor={actor}
            datastore={datastore}
            target={target}
            verb={verb}
          />
        }
        description={moment(timestamp).fromNow()}
      />
    </List.Item>
  )
}

export default DatastoreActivityItem
