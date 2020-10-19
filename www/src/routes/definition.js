import DefinitionIndexes from "pages/DatastoreDefinition/DefinitionIndexes"
import DefinitionColumns from "pages/DatastoreDefinition/DefinitionColumns"
import DefinitionOverview from "pages/DatastoreDefinition/DefinitionOverview"
import DefinitionHistory from "pages/DatastoreDefinition/DefinitionHistory"
import DefinitionDiscussions from "pages/DatastoreDefinition/DefinitionDiscussions"
import DefinitionReadmeEditor from "pages/DatastoreDefinition/DefinitionReadmeEditor"
import DefinitionColumnReadmeEditor from "pages/DatastoreDefinition/DefinitionColumnReadmeEditor"

export default [
  {
    component: DefinitionReadmeEditor,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/readme/edit",
    namespace: "datastores",
  },
  {
    component: DefinitionColumnReadmeEditor,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/columns/:columnName/readme/edit",
    namespace: "datastores",
  },
  {
    component: DefinitionHistory,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/history",
    namespace: "datastores",
  },
  {
    component: DefinitionIndexes,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/indexes",
    namespace: "datastores",
  },
  {
    component: DefinitionColumns,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/columns",
    namespace: "datastores",
  },
  {
    component: DefinitionDiscussions,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/discussions",
    namespace: "datastores",
  },
  {
    component: DefinitionOverview,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/overview",
    namespace: "datastores",
  },
]
