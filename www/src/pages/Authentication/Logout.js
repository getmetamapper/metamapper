import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { Spin } from "antd"
import { AUTH_TOKEN, WORKSPACE_TOKEN } from "lib/constants"

class Logout extends Component {
  constructor(props) {
    super(props)

    window.localStorage.removeItem(AUTH_TOKEN)
    window.localStorage.removeItem(WORKSPACE_TOKEN)
  }

  componentDidMount() {
    window.location.href = "/login"
  }

  render() {
    return (
      <div className="redirection-component">
        <Helmet>Logging you out...</Helmet>
        <Spin size="large" />
      </div>
    )
  }
}

export default Logout
