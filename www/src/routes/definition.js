import DefinitionIndexes from "pages/DatastoreDefinition/DefinitionIndexes"
import DefinitionColumns from "pages/DatastoreDefinition/DefinitionColumns"
import DefinitionOverview from "pages/DatastoreDefinition/DefinitionOverview"
import DefinitionHistory from "pages/DatastoreDefinition/DefinitionHistory"
import DefinitionDiscussions from "pages/DatastoreDefinition/DefinitionDiscussions"
import DefinitionReadmeEditor from "pages/DatastoreDefinition/DefinitionReadmeEditor"


export default [
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
    component: DefinitionReadmeEditor,
    path:
      "/:workspaceSlug/datastores/:datastoreSlug/definition/:schemaName/:tableName/readme/edit",
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
