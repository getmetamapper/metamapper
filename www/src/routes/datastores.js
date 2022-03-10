import Datastores from "pages/Datastores/Datastores"
import DatastoreSetup from "pages/Datastores/DatastoreSetup"
import Overview from "pages/DatastoreSettings/DatastoreOverview"
import Assets from "pages/DatastoreSettings/DatastoreAssets"
import RunHistory from "pages/DatastoreSettings/RunHistory"
import ConnectionSettings from "pages/DatastoreSettings/ConnectionSettings"
import Access from "pages/DatastoreSettings/DatastoreAccess"
import DatastoreSettings from "pages/DatastoreSettings/DatastoreSettings"

export default [
  {
    component: Datastores,
    path: "/:workspaceSlug/datastores",
    exact: true,
    namespace: "datastores",
  },
  {
    component: DatastoreSetup,
    path: "/:workspaceSlug/datastores/new",
    exact: true,
    namespace: "datastore-setup",
  },
  {
    component: DatastoreSettings,
    path: "/:workspaceSlug/datastores/:datastoreSlug/settings",
    namespace: "datastores",
  },
  {
    component: Access,
    path: "/:workspaceSlug/datastores/:datastoreSlug/access",
    namespace: "datastores",
  },
  {
    component: ConnectionSettings,
    path: "/:workspaceSlug/datastores/:datastoreSlug/connection",
    namespace: "datastores",
  },
  {
    component: RunHistory,
    path: "/:workspaceSlug/datastores/:datastoreSlug/runs",
    namespace: "datastores",
  },
  {
    component: Assets,
    path: "/:workspaceSlug/datastores/:datastoreSlug/assets",
    namespace: "datastores",
  },
  {
    component: Overview,
    path: "/:workspaceSlug/datastores/:datastoreSlug",
    namespace: "datastores",
  },
]
