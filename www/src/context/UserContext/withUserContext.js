import React from "react"
import { Consumer } from "./context"

export default function withUserContext(Component) {
  return class WithUserContext extends React.Component {
    static displayName = `WithUserContext(Component)`

    render() {
      return (
        <Consumer>
          {({
            refreshUser,
            currentUser,
            currentWorkspace,
            myWorkspaces,
            config,
          }) => (
            <Component
              currentUser={currentUser}
              currentWorkspace={currentWorkspace}
              config={config}
              myWorkspaces={myWorkspaces}
              refreshUser={refreshUser}
              {...this.props}
            />
          )}
        </Consumer>
      )
    }
  }
}
