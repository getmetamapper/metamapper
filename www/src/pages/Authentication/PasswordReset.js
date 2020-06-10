import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Row } from "antd"
import AuthForm from "app/Authentication/AuthForm"
import PasswordResetForm from "app/Authentication/PasswordResetForm"
import ResetPassword from "graphql/mutations/ResetPassword"

class PasswordReset extends Component {
  constructor(props) {
    super(props)

    this.links = [
      {
        to: "/login",
        prompt: "Remember your password?",
        text: "Sign in.",
      },
    ]
  }

  handleSuccess = ({ data }) => {
    return {
      submitting: false,
      alert: {
        type: "success",
        message: "Help is on the way.",
        description: (
          <span>
            We have sent an email with instructions to reset your password.
          </span>
        ),
      },
    }
  }

  handleError = () => {
    return {
      submitting: false,
      alert: {
        type: "error",
        message: "Whoops.",
        description: (
          <span>
            We aren't sure if this account exists.
          </span>
        ),
      },
    }
  }

  render() {
    const { mutate } = this.props
    return (
      <section className="password-reset">
        <Helmet>
          <title>Reset Your Password - Metamapper</title>
          <script
            type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/zxcvbn/4.4.2/zxcvbn.js"
            secure
          />
        </Helmet>
        <Row>
          <Col span={6} offset={9}>
            <AuthForm
              title="Reset Your Password"
              mutate={mutate}
              component={PasswordResetForm}
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

export default graphql(ResetPassword)(PasswordReset)
