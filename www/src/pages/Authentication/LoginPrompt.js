import React, { Component } from "react"
import { Col, Row } from "antd"
import { graphql, compose } from "react-apollo"
import { Helmet } from "react-helmet"
import { withRouter } from "react-router-dom"
import CheckUserExists from "graphql/mutations/CheckUserExists"
import TriggerSingleSignOn from "graphql/mutations/TriggerSingleSignOn"
import AuthForm from "app/Authentication/AuthForm"
import LoginPromptForm from "app/Authentication/LoginPromptForm"

class LoginPrompt extends Component {
  constructor(props) {
    super(props)

    this.links = [
      {
        to: "/login/email",
        text: "(skip to sign in page)",
      },
    ]
  }

  handleSuccess = ({ data }) => {
    const { email, ok, isSSOForced, workspaceSlug } = data.userExistsCheck

    if (ok) {
      // Redirect
      if (isSSOForced && workspaceSlug) {
        this.props.history.push(`/login/sso/${workspaceSlug}`)
      } else {
        this.props.history.push(`/login/email?email=${email}`)
      }
    } else {
      this.props.history.push(`/signup?email=${email}`)
    }
  }

  render() {
    const { checkUserExists } = this.props
    return (
      <section className="login-prompt">
        <Helmet>
          <title>Log In - Metamapper</title>
        </Helmet>
        <Row>
          <Col span={6} offset={9}>
            <AuthForm
              title="Let's Get Started"
              mutate={checkUserExists}
              component={LoginPromptForm}
              onSuccess={this.handleSuccess}
              links={this.links}
              timeout={500}
            />
          </Col>
        </Row>
      </section>
    )
  }
}

export default compose(
  withRouter,
  graphql(CheckUserExists, { name: "checkUserExists" }),
  graphql(TriggerSingleSignOn, { name: "triggerSSO" })
)(LoginPrompt)
