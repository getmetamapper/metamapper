import React, { Component } from "react"
import { compose } from "react-apollo"
import { Spin } from "antd"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"

class Home extends Component {
  componentWillMount() {
    const { config, currentWorkspace, history } = this.props

    const datastoreSlug = config.getDatastoreSlug()

    if (!currentWorkspace) {
      history.push("/workspaces")
    } else if (currentWorkspace && datastoreSlug) {
      history.push(`/${currentWorkspace.slug}/datastores/${datastoreSlug}`)
    } else {
      history.push(`/${currentWorkspace.slug}/datastores`)
    }
  }

  render() {
    return (
      <div style={{ textAlign: "center" }}>
        <Spin size="large" />
      </div>
    )
  }
}

export default compose(withRouter, withUserContext)(Home)
