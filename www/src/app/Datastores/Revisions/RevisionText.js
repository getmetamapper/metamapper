import React, { Fragment } from "react"
import { Tag } from "antd"
import { map } from "lodash"
import { humanize } from "lib/utilities"

const humanizeFieldName = (fieldName) => {
  const fieldMap = {
    name: "Name",
    ordinal_position: "Position",
    data_type: "Data type",
    max_length: "Max length",
    numeric_scale: "Numeric scale",
    is_nullable: "Nullable constraint",
    is_primary: "Primary key constraint",
    is_unique: "Uniqueness constraint",
    sql: "SQL",
  }

  if (fieldName in fieldMap) {
    return fieldMap[fieldName]
  }

  return humanize(fieldName)
}

const displayChangedValue = (field, value, color) => {
  if (typeof value === "boolean") {
    value = value.toString()
  }
  else if (value === null || value === undefined) {
    value = "null"
  }

  if (field === "columns") {
    return (
      <Fragment>
        {map(value, ({ column_name }) => <Tag color={color}>{column_name}</Tag>)}
      </Fragment>
    )
  }

  return <Tag color={color}>{value}</Tag>
}

const resourceDecorator = (parentResource, relatedResource, color) => (
  <span style={{ color }}>
    {parentResource && `${parentResource.label}.`}
    <b>{relatedResource && `${relatedResource.label}`}</b>
  </span>
)

const CreatedRevision = ({ parentResource, relatedResource }) => (
  <>
    <span className="mr-10">
      {relatedResource && relatedResource.type}{" "}
      {resourceDecorator(parentResource, relatedResource, "#52c41a")} was added.
    </span>
  </>
)

const ModifiedRevision = ({
  parentResource,
  relatedResource,
  metadata: { field, old_value, new_value },
}) => (
  <span className="modified-table-revision">
    <span className="mr-10">
      {humanizeFieldName(field)} for {relatedResource && relatedResource.type.toLowerCase()}{" "}
      {resourceDecorator(parentResource, relatedResource, "#faad14")} changed:
    </span>
    {displayChangedValue(field, old_value, "red")}
    {displayChangedValue(field, new_value, "green")}
  </span>
)

const DroppedRevision = ({ parentResource, relatedResource }) => (
  <>
    <span className="mr-10">
      {relatedResource && relatedResource.type}{" "}
      {resourceDecorator(parentResource, relatedResource, "#f5222d")} was
      dropped.
    </span>
  </>
)

export const renderRevisionText = (revision) => {
  if (!revision) return null

  const switchBoard = {
    "A_1": CreatedRevision,
    "A_2": ModifiedRevision,
    "A_3": DroppedRevision,
  }

  const Component = switchBoard[revision.action]

  return <Component {...revision} />
}
