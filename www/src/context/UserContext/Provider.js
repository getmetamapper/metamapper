import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { find } from "lodash"
import { withRouter } from "react-router-dom"
import gql from "graphql-tag"
import { USER_ID, WORKSPACE_TOKEN } from "lib/constants"
import withLoader from "hoc/withLoader"
import { UserConfiguration } from "lib/user-config"
import { Provider } from "./context"

class UserProvider extends Component {
  static getDerivedStateFromProps(
    { refreshUser, currentUser, myWorkspaces, match: { params } },
    state
  ) {
    if (!currentUser) return null

    const config = new UserConfiguration(currentUser)

    let currentWorkspace = config.getCurrentWorkspace()

    // If there is a workspaceSlug in the URL, we need to switch to that context.
    if (params.hasOwnProperty("workspaceSlug")) {
      const workspace = find(myWorkspaces, { slug: params.workspaceSlug })

      if (workspace) {
        currentWorkspace = workspace
      }
    }

    // If no workspace exists, just pick the first one on the list.
    if (!currentWorkspace && myWorkspaces.length >= 1) {
      currentWorkspace = config.setCurrentWorkspace(myWorkspaces[0])
    }

    if (currentWorkspace) {
      const { pk } = currentWorkspace
      const workspace = find(myWorkspaces, { pk })

      // Set the X-Workspace-Id header token. This is used to scope
      // GraphQL requests to the current workspace.
      if (workspace !== undefined) {
        localStorage.setItem(WORKSPACE_TOKEN, pk)
      } else {
        currentWorkspace = config.removeCurrentWorkspace()
      }

      if (workspace) {
        currentWorkspace = config.setCurrentWorkspace(workspace)
        // If we have a matched workspace, but no membership, we
        // need to refetch the user. This happens sometimes when we
        // switch workspaces.
        if (!currentUser.currentMembership) {
          refreshUser()
        }
      }
    }

    localStorage.setItem(USER_ID, currentUser.pk)

    return {
      value: {
        config,
        currentUser,
        currentWorkspace,
        myWorkspaces,
        refreshUser,
      },
    }
  }

  static defaultProps = {
    refreshUser: () => {},
  }

  state = {
    value: {
      currentUser: this.props.currentUser,
      refreshUser: this.props.refreshUser,
    },
  }

  render() {
    return <Provider value={this.state.value}>{this.props.children}</Provider>
  }
}

const currentUser = graphql(
  gql`
    query currentUser {
      me {
        id
        pk
        fname
        lname
        email
        currentMembership {
          permissions
        }
      }
      myWorkspaces {
        edges {
          node {
            id
            pk
            name
            slug
          }
        }
      }
    }
  `,
  {
    options: () => ({ errorPolicy: "ignore" }),
    props: ({ data, location, match }) => {
      const result = {
        loading: data && data.loading,
        errored: data && data.error,
        refreshUser: data && data.refetch,
        currentUser: null,
        myWorkspaces: [],
      }

      if (!data || data.loading || data.error) {
        return result
      }

      let workspaces = []
      const { myWorkspaces } = data

      if (myWorkspaces && myWorkspaces.hasOwnProperty("edges")) {
        workspaces = myWorkspaces.edges.map(({ node }) => {
          return node
        })
      }

      return {
        loading: data.loading,
        refreshUser: data.refetch,
        currentUser: data.me,
        myWorkspaces: workspaces,
      }
    },
  },
)

const withSpinLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

export default compose(currentUser, withRouter, withSpinLoader)(UserProvider)
