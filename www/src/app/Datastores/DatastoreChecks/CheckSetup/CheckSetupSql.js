import React from "react"
import { Input } from "antd"
import CodeEditor from "app/Common/CodeEditor"
import CheckSqlPreviewResults from "app/Datastores/DatastoreChecks/CheckSqlPreviewResults"

const CheckSetupSql = ({
  form: { getFieldDecorator },
  sqlText,
  sqlException,
  queryResults,
  onChange,
}) => (
  <>
    {getFieldDecorator(
      "queryId",
      {}
    )(
      <Input type="hidden" />
    )}
    <CodeEditor
      mode="sql"
      value={sqlText}
      onChange={onChange}
    />
    <CheckSqlPreviewResults
      queryResults={queryResults}
      sqlException={sqlException}
    />
  </>
)

export default CheckSetupSql
