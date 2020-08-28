import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withRouter } from "react-router"
import { Spin } from "antd"
import { setTokenAndGetRedirectUri } from "lib/utilities"
import { AUTH_TOKEN, WORKSPACE_TOKEN } from "lib/constants"
import LoginWithSSOTokenMutation from "graphql/mutations/LoginWithSSOToken"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"

class LoginWithToken extends Component {
  componentWillMount() {
    window.localStorage.removeItem(AUTH_TOKEN)
    window.localStorage.removeItem(WORKSPACE_TOKEN)
  }

  componentDidMount() {
    const {
      match: {
        params: { uid, singleUseToken: token, workspaceSlug },
      },
    } = this.props

    this.props
      .mutate({
        variables: {
          uid,
          token,
          workspaceSlug,
        },
      })
      .then(({ data: { loginWithSSOToken } }) => {
        const { jwt: token } = loginWithSSOToken

        if (token) {
          window.location.href = setTokenAndGetRedirectUri(token, `/${workspaceSlug}`)
        }
      })
  }

  render() {
    return (
      <div className="logout">
        <Spin />
      </div>
    )
  }
}

export default compose(
  withRouter,
  withGetWorkspaceBySlug,
  graphql(LoginWithSSOTokenMutation)
)(LoginWithToken)
