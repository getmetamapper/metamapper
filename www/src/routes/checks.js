import Check from "pages/DatastoreChecks/DatastoreCheck"
import CheckSetup from "pages/DatastoreChecks/DatastoreCheckSetup"
import CheckSqlEditor from "pages/DatastoreChecks/DatastoreCheckSqlEditor"
import CheckAlertRuleSetup from "pages/DatastoreChecks/DatastoreCheckAlertRuleSetup"
import CheckAlertRuleEdit from "pages/DatastoreChecks/DatastoreCheckAlertRuleEdit"

export default [
  {
    component: CheckSetup,
    path: "/:workspaceSlug/datastores/:datastoreSlug/checks/new",
    namespace: "check-editor",
  },
  {
    component: CheckSqlEditor,
    path: "/:workspaceSlug/datastores/:datastoreSlug/checks/:checkId/sql/edit",
    namespace: "check-editor",
  },
  {
    component: CheckAlertRuleEdit,
    path: "/:workspaceSlug/datastores/:datastoreSlug/checks/:checkId/alerts/rules/:ruleId/edit",
    namespace: "check-alert-rule-edit",
  },
  {
    component: CheckAlertRuleSetup,
    path: "/:workspaceSlug/datastores/:datastoreSlug/checks/:checkId/alerts/rules/new",
    namespace: "check-alert-rule-setup",
  },
  {
    component: Check,
    path: "/:workspaceSlug/datastores/:datastoreSlug/checks/:checkId",
    namespace: "checks",
  },
]
