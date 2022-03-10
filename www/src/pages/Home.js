import React, { Component } from "react"
import { compose } from "react-apollo"
import { Spin } from "antd"
import { withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"

class Home extends Component {
  componentWillMount() {
    const {
      config,
      currentWorkspace,
    } = this.props

    const datastoreSlug = config.getDatastoreSlug()

    if (datastoreSlug) {
      this.props.history.push(`/${currentWorkspace.slug}/datastores/${datastoreSlug}`)
    } else {
      this.props.history.push(`/${currentWorkspace.slug}/datastores`)
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
