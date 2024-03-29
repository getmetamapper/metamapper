import React, { Component } from "react"
import { compose } from "react-apollo"
import { find } from "lodash"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { AUTH_TOKEN } from "lib/constants"

export default (
  ChildComponent,
  isProtected = true,
  ignoreRedirects = false,
  shouldRefreshUser = false,
) => {
  class ComposedComponent extends Component {
    // Our component just got rendered
    componentDidMount() {
      if (!ignoreRedirects) {
        this.shouldNavigateAway()
      }
    }

    // Our component just got updated
    componentDidUpdate() {
      if (!ignoreRedirects) {
        this.shouldNavigateAway()
      }
    }

    shouldNavigateAway() {
      const { href, pathname } = window.location
      const { config, currentUser, myWorkspaces } = this.props
      const {
        match: { params },
      } = this.props

      const authToken = localStorage.getItem(AUTH_TOKEN)

      if (shouldRefreshUser || (authToken && !currentUser) || (!authToken && currentUser)) {
        this.props.refreshUser()
      }

      let { currentWorkspace } = this.props
      if (config) {
        currentWorkspace = config.getCurrentWorkspace()
      }

      // Force reload to capture current workspace if the URL doesn't match.
      if (currentUser && params.hasOwnProperty("workspaceSlug")) {
        const workspace = find(myWorkspaces, { slug: params.workspaceSlug })

        if (!currentWorkspace && workspace) {
          config.setCurrentWorkspace(workspace)
        }

        if (!currentWorkspace && !workspace && !href.includes("workspaces")) {
          this.props.history.push("/workspaces")
        }

        if (
          currentWorkspace &&
          workspace &&
          currentWorkspace.slug !== workspace.slug
        ) {
          config.setCurrentWorkspace(workspace)
        }
      }

      // If login screen, redirect to the dashboard.
      if (!isProtected && currentUser) {
        this.props.history.push("/")
      }

      // If it is a restricted route and currentUser is
      // not authenticated, redirect to Login page.
      if (isProtected && !currentUser && pathname !== "/login") {
        this.props.history.push(`/login?next=${encodeURIComponent(window.location.href)}`)
      } else if (
        isProtected &&
        !currentWorkspace &&
        !href.includes("workspaces")
      ) {
        window.location.href = "/workspaces"
      }
    }

    render() {
      return <ChildComponent {...this.props} />
    }
  }
  return compose(withRouter, withUserContext)(ComposedComponent)
}
