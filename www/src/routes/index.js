import authentication from "./authentication"
import workspaces from "./workspaces"
import datastores from "./datastores"
import definition from "./definition"
import omnisearch from "./omnisearch"

const routes = [authentication, workspaces, definition, datastores, omnisearch]

export default [].concat(...routes)
