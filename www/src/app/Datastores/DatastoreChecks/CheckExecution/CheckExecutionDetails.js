import React from "react"
import { compose } from "react-apollo"
import { Alert, Drawer } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import CheckQueryText from "app/Datastores/DatastoreChecks/CheckQueryText"
import ExecutionMetadata from "app/Datastores/DatastoreChecks/CheckExecution/CheckExecutionMetadata"
import ExecutionResults from "app/Datastores/DatastoreChecks/CheckExecution/CheckExecutionResults"
import withGetCheckExecution from "graphql/withGetCheckExecution"

const defaultDrawerProps = {
  placement: "right",
  title: "Check Execution",
  width: 800,
}

const ExecutionDetails = ({
  checkExecution,
  visible,
  onClose,
}) => (
  <Drawer visible={visible} onClose={onClose} {...defaultDrawerProps}>
    {checkExecution.error && (
      <div className="check-execution-error">
        <Alert
          showIcon
          message={<code>{checkExecution.error}</code>}
          type="error"
        />
      </div>
    )}
    <div className="check-execution-metadata">
      <ExecutionMetadata {...checkExecution} />
    </div>
    <div className="check-execution-query">
      <CheckQueryText hasFooter sqlText={checkExecution.executedQueryText} />
    </div>
    <div className="check-execution-expectations">
      <ExecutionResults results={checkExecution.expectationResults} />
    </div>
  </Drawer>
)

ExecutionDetails.defaultProps = {
  checkExecution: {
    error: null
  }
}

export default compose(withGetCheckExecution, withLargeLoader)(ExecutionDetails)
