import React from "react"
import { Link as BaseLink } from "react-router-dom"
import { withUserContext } from "context/UserContext"

const toLinkHelper = (prepend, workspace, to) => {
  if (prepend && workspace && workspace.hasOwnProperty("slug")) {
    return `/${workspace.slug}${to}`
  }
  return to
}

const Link = ({
  currentWorkspace,
  currentUser,
  myWorkspaces,
  refreshUser,
  config,
  prependWorkspace,
  to,
  ...restProps
}) => {
  let workspace = config.getCurrentWorkspace()
  if (!workspace) {
    workspace = currentWorkspace
  }
  return (
    <BaseLink to={toLinkHelper(prependWorkspace, workspace, to)} {...restProps} />
  )
}

Link.defaultProps = {
  prependWorkspace: true,
}

export default withUserContext(Link)
