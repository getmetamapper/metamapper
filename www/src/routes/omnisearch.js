import Omnisearch from "pages/Omnisearch/Omnisearch"
import OmnisearchResults from "pages/Omnisearch/OmnisearchResults"

export default [
  {
    component: Omnisearch,
    path: "/:workspaceSlug/search",
    exact: true,
    namespace: "omnisearch",
  },
  {
    component: Omnisearch,
    path: "/:workspaceSlug/",
    exact: true,
    namespace: "omnisearch",
  },
  {
    component: OmnisearchResults,
    path: "/:workspaceSlug/search/results",
    exact: true,
    namespace: "omnisearch",
  },
]
