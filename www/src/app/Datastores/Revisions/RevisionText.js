import React, { Fragment } from "react"
import { Tag } from "antd"
import { map } from "lodash"
import { humanize } from "lib/utilities"
import Link from "app/Navigation/Link"

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
    db_comment: "Database comment",
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

/*
 * Created Revision Handlers
 */

const renderSchemaOnCreate = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Schema named <b>{label}</b> was created.
  </Fragment>
)

const renderTableOnCreate = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Table named <b>{label}</b> was added to the <Link to={pathname}>{parentLabel}</Link> schema.
  </Fragment>
)

const renderColumnOnCreate = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Column named <b>{label}</b> was added to the <Link to={pathname}>{parentLabel}</Link> table.
  </Fragment>
)

const renderIndexOnCreate = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Index named <b>{label}</b> was added to the <Link to={pathname}>{parentLabel}</Link> table.
  </Fragment>
)

const createHandlers = {
  "Schema": renderSchemaOnCreate,
  "Table": renderTableOnCreate,
  "Column": renderColumnOnCreate,
  "Index": renderIndexOnCreate,
}

const CreatedRevisionHandler = ({ relatedResource }) => (
  <Fragment>
    <span className="mr-10">
      {createHandlers[relatedResource.type](relatedResource)}
    </span>
  </Fragment>
)

/*
 * Modified Revision Handlers
 */

const renderSchemaOnModify = ({ field, old_value, new_value }, { label, parentLabel, pathname }) => (
  <span className="modified-table-revision">
    <span className="mr-10">
      {humanizeFieldName(field)} for the schema <b>{label}</b> has changed:
    </span>
    {displayChangedValue(field, old_value, "red")}
    {displayChangedValue(field, new_value, "green")}
  </span>
)

const renderTableOnModify = ({ field, old_value, new_value }, { label, parentLabel, pathname }) => (
  <span className="modified-table-revision">
    <span className="mr-10">
      {humanizeFieldName(field)} for the <b>{label}</b> table in the <Link to={pathname}>{parentLabel}</Link> schema has changed:
    </span>
    {displayChangedValue(field, old_value, "red")}
    {displayChangedValue(field, new_value, "green")}
  </span>
)

const renderColumnOnModify = ({ field, old_value, new_value }, { label, parentLabel, pathname }) => (
  <span className="modified-table-revision">
    <span className="mr-10">
      {humanizeFieldName(field)} for the <b>{label}</b> column in the <Link to={pathname}>{parentLabel}</Link> table has changed:
    </span>
    {displayChangedValue(field, old_value, "red")}
    {displayChangedValue(field, new_value, "green")}
  </span>
)

const renderIndexOnModify = ({ field, old_value, new_value }, { label, parentLabel, pathname }) => (
  <span className="modified-table-revision">
    <span className="mr-10">
      {humanizeFieldName(field)} for the <b>{label}</b> index in the <Link to={pathname}>{parentLabel}</Link> table has changed:
    </span>
    {displayChangedValue(field, old_value, "red")}
    {displayChangedValue(field, new_value, "green")}
  </span>
)

const modifiedHandlers = {
  "Schema": renderSchemaOnModify,
  "Table": renderTableOnModify,
  "Column": renderColumnOnModify,
  "Index": renderIndexOnModify,
}

const ModifiedRevisionHandler = ({ metadata, relatedResource }) => (
  <Fragment>
    <span className="mr-10">
      {modifiedHandlers[relatedResource.type](metadata, relatedResource)}
    </span>
  </Fragment>
)

/*
 * Dropped Revision Handlers
 */

const renderSchemaOnDrop = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Schema named <b>{label}</b> was dropped.
  </Fragment>
)

const renderTableOnDrop = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Table named <b>{label}</b> was dropped from the <Link to={pathname}>{parentLabel}</Link> schema.
  </Fragment>
)

const renderColumnOnDrop = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Column named <b>{label}</b> was dropped from the <Link to={pathname}>{parentLabel}</Link> table.
  </Fragment>
)

const renderIndexOnDrop = ({ label, parentLabel, pathname }) => (
  <Fragment>
    Index named <b>{label}</b> was dropped from the <Link to={pathname}>{parentLabel}</Link> table.
  </Fragment>
)

const droppedHandlers = {
  "Schema": renderSchemaOnDrop,
  "Table": renderTableOnDrop,
  "Column": renderColumnOnDrop,
  "Index": renderIndexOnDrop,
}

const DroppedRevisionHandler = ({ relatedResource }) => (
  <Fragment>
    <span className="mr-10">
      {droppedHandlers[relatedResource.type](relatedResource)}
    </span>
  </Fragment>
)


export const renderRevisionText = (revision) => {
  if (!revision) return null

  const switchBoard = {
    "A_1": CreatedRevisionHandler,
    "A_2": ModifiedRevisionHandler,
    "A_3": DroppedRevisionHandler,
  }

  const Component = switchBoard[revision.action]

  return (
    <span className={`revision-${revision.action}`}>
      <Component {...revision} />
    </span>
  )
}
