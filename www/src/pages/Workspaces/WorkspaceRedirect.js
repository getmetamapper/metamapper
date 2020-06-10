import React, { Component } from "react"

class WorkspaceRedirect extends Component {
  componentWillMount() {
    const { config } = this.props

    if (config) {
      const workspace = config.getCurrentWorkspace()

      if (workspace) {
        this.props.history.push(`/${workspace.slug}`)
        return null
      }
    }

    this.props.history.push("/")
  }

  render() {
    return <div>Redirecting...</div>
  }
}

export default WorkspaceRedirect
