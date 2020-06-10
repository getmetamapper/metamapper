import React from "react"

const defaultState = {
  refreshUser: () => true,
  currentUser: null,
  currentWorkspace: null,
  myWorkspaces: [],
}

const { Provider, Consumer } = React.createContext(defaultState)

export { Provider, Consumer, defaultState }
