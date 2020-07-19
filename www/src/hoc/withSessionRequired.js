import React, { Component } from "react"
import { compose } from "react-apollo"
import { find } from "lodash"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { AUTH_TOKEN } from "lib/constants"

export default (
  ChildComponent,
  isProtected = true,
  ignoreRedirects = false
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
      const { href } = window.location
      const { config, currentUser, myWorkspaces } = this.props
      const {
        match: { params },
      } = this.props

      let { currentWorkspace } = this.props
      if (config) {
        currentWorkspace = config.getCurrentWorkspace()
      }

      // Force reload to capture current workspace if the URL doesn't match.
      if (params.hasOwnProperty("workspaceSlug")) {
        const workspace = find(myWorkspaces, { slug: params.workspaceSlug })

        if (!currentWorkspace && workspace) {
          config.setCurrentWorkspace(workspace)
        }

        if (!currentWorkspace && !workspace) {
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

      this.props.refreshUser()

      if (localStorage.getItem(AUTH_TOKEN) && !currentUser) {
        return null;
      }

      // If login screen, redirect to the dashboard.
      if (!isProtected && currentUser) {
        this.props.history.push("/")
      }

      // If it is a restricted route and currentUser is
      // not authenticated, redirect to Login page.
      if (isProtected && !currentUser) {
        this.props.history.push("/login")
      } else if (
        isProtected &&
        !currentWorkspace &&
        !href.includes("workspaces")
      ) {
        this.props.history.push("/workspaces")
      }
    }

    render() {
      return <ChildComponent {...this.props} />
    }
  }
  return compose(withRouter, withUserContext)(ComposedComponent)
}
