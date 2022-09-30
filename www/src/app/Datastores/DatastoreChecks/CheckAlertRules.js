import React from "react"
import { compose } from "react-apollo"
import { Button } from "antd"
import { withRouter } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import Link from "app/Navigation/Link"
import CheckAlertRulesTable from "app/Datastores/DatastoreChecks/CheckAlertRulesTable"
import withGetCheckAlertRules from "graphql/withGetCheckAlertRules"

const CheckAlertRules = ({
  checkAlertRules,
  loading,
  match: {
    params: { datastoreSlug, checkId },
  },
}) => (
  <div className="check-alert-rules">
    <h2>
      Alert Rules
    </h2>
    <Link to={`/datastores/${datastoreSlug}/checks/${checkId}/alerts/rules/new`}>
      <Button type="primary">
        Create Alert
      </Button>
    </Link>
    <CheckAlertRulesTable
      rules={checkAlertRules}
      loading={loading}
    />
  </div>
)

export default compose(
  withRouter,
  withGetCheckAlertRules,
  withLargeLoader,
)(CheckAlertRules)
