import OmnisearchResults from "pages/Omnisearch/OmnisearchResults"

export default [
  {
    component: OmnisearchResults,
    path: "/:workspaceSlug/search/results",
    exact: true,
    namespace: "omnisearch",
  },
]
