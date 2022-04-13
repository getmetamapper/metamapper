import authentication from "./authentication"
import workspaces from "./workspaces"
import datastores from "./datastores"
import definition from "./definition"
import checks from "./checks"
import omnisearch from "./omnisearch"

const routes = [
    authentication,
    workspaces,
    definition,
    checks,
    datastores,
    omnisearch,
];

export default [].concat(...routes)
