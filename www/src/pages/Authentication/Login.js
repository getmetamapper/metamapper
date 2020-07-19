import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Row } from "antd"
import { Link } from "react-router-dom"
import { setTokenAndGetRedirectUri } from "lib/utilities"
import AuthenticateUser from "graphql/mutations/AuthenticateUser"
import AuthForm from "app/Authentication/AuthForm"
import LoginForm from "app/Authentication/LoginForm"

class Login extends Component {
  constructor(props) {
    super(props)

    this.links = [
      {
        to: "/password/reset",
        prompt: "Forgot your password?",
        text: "Reset it here.",
      },
      {
        to: "/signup",
        prompt: "Need an account?",
        text: "Sign up.",
      },
    ]
  }

  handleSuccess = ({ data }) => {
    const { token } = data.tokenAuth
    if (token) {
      this.props.history.push(setTokenAndGetRedirectUri(token))
    }
  }

  handleError = () => {
    return {
      submitting: false,
      alert: {
        type: "error",
        message: "Incorrect login credentials.",
        description: (
          <span>
            Do you need help <Link to="/password/reset">logging in?</Link>
          </span>
        ),
      },
    }
  }

  render() {
    const { mutate } = this.props
    return (
      <section className="login">
        <Helmet>
          <title>Log In - Metamapper</title>
        </Helmet>
        <Row>
          <Col span={6} offset={9}>
            <AuthForm
              title="Let's Get Started"
              mutate={mutate}
              component={LoginForm}
              onSuccess={this.handleSuccess}
              onError={this.handleError}
              links={this.links}
            />
          </Col>
        </Row>
      </section>
    )
  }
}

export default graphql(AuthenticateUser)(Login)
