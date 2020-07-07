import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { Spin } from "antd"

class WorkspaceRedirect extends Component {
  constructor(props) {
    super(props)

    this.redirect = this.redirect.bind(this)
  }

  componentWillMount() {
    setTimeout(this.redirect, 750)
  }

  redirect() {
    const { config, currentUser } = this.props

    if (config) {
      const workspace = config.getCurrentWorkspace()

      if (workspace) {
        this.props.history.push(`/${workspace.slug}`)
        return null
      }
    }

    if (currentUser) {
      this.props.history.push("/")
    }
  }

  render() {
    return (
      <div className="redirection-component">
        <Helmet>Redirecting...</Helmet>
        <Spin size="large" />
      </div>
    )
  }
}

export default WorkspaceRedirect
