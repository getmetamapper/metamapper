import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Spin, Icon } from "antd"
import { withRouter } from "react-router-dom"
import TriggerSingleSignOn from "graphql/mutations/TriggerSingleSignOn"

class SingleSignOnRedirect extends Component {
  componentWillMount() {
    const {
      match: {
        params: { workspaceSlug },
      },
    } = this.props

    const httpRequest = this.props.mutate({
      variables: {
        workspaceSlug,
      },
    })

    httpRequest.then(this.handleSuccess)
  }

  handleSuccess = ({ data: { triggerSingleSignOn } }) => {
    const { redirectUrl } = triggerSingleSignOn

    if (redirectUrl) {
      setTimeout(() => {
        window.location.href = redirectUrl
      }, 1000)
    } else {
      window.location.href = "/login/sso"
    }
  }

  render() {
    return (
      <div
        style={{
          textAlign: "center",
          marginTop: 120,
          fontSize: 16,
        }}
      >
        <p>
          <Spin indicator={<Icon type="loading" />} size="large" />
        </p>
        <p style={{ color: "#64b7fe" }}>
          Redirecting to your single sign-on provider.
        </p>
      </div>
    )
  }
}

export default compose(
  withRouter,
  graphql(TriggerSingleSignOn)
)(SingleSignOnRedirect)
