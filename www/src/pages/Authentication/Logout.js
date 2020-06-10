import React, { Component } from "react"
import { withRouter } from "react-router"
import { Helmet } from "react-helmet"
import { withUserContext } from "context/UserContext"
import { Spin } from "antd"
import { AUTH_TOKEN, WORKSPACE_TOKEN } from "lib/constants"

class Logout extends Component {
  constructor(props) {
    super(props)

    window.localStorage.removeItem(AUTH_TOKEN)
    window.localStorage.removeItem(WORKSPACE_TOKEN)

    this.redirect = this.redirect.bind(this)
  }

  componentDidMount() {
    setTimeout(this.redirect, 1000);
  }

  redirect() {
    window.location.href = '/login'
  }

  render() {
    return (
      <div className="logout">
        <Helmet>Logging you out...</Helmet>
        <Spin />
      </div>
    )
  }
}

export default withRouter(withUserContext(Logout))
