import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Row, message } from "antd"
import ResetPasswordConfirm from "graphql/mutations/ResetPasswordConfirm"
import AuthForm from "app/Authentication/AuthForm"
import PasswordConfirmForm from "app/Authentication/PasswordConfirmForm"

class PasswordConfirm extends Component {
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
    this.props.history.push("/login")

    message.success("Your password has been reset.")
  }

  handleError = ({ data }) => {
    return {
      submitting: false,
      alert: {
        type: "error",
        message: "Malfunction.",
        description: (
          <span>
            We could not process your request.
          </span>
        ),
      },
    }
  }

  render() {
    const { mutate } = this.props
    return (
      <section className="password-confirm">
        <Helmet>
          <title>Update Your Password - Metamapper</title>
          <script
            type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/zxcvbn/4.4.2/zxcvbn.js"
            secure
          />
        </Helmet>
        <Row>
          <Col span={6} offset={9}>
            <AuthForm
              title="Update Your Password"
              mutate={mutate}
              component={PasswordConfirmForm}
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

export default graphql(ResetPasswordConfirm)(PasswordConfirm)
