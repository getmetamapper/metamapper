import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Row, message } from "antd"
import { getErrorDefinition, setTokenAndGetRedirectUri } from "lib/utilities"
import yaml from "js-yaml"
import AuthForm from "app/Authentication/AuthForm"
import SignupForm from "app/Authentication/SignupForm"
import RegisterUser from "graphql/mutations/RegisterUser"

class Signup extends Component {
  state = { errorDefinition: {} }

  constructor(props) {
    super(props)

    getErrorDefinition('en').then(txt => {
      const {
        errors: errorDefinitions,
      } = yaml.safeLoad(txt)

      this.setState({ errorDefinitions })
    })

    this.links = [
      {
        to: "/login",
        prompt: "Already have an account?",
        text: "Sign in.",
      },
    ]
  }

  handleSuccess = ({ data }) => {
    const { user, jwt, errors } = data.registerUser

    if (errors && errors.length > 0) {
      return this.handleError({ data })
    }

    if (jwt) {
      this.props.refreshUser()
      this.props.history.push(setTokenAndGetRedirectUri(jwt))
    } else {
      this.props.history.push(`/login?${user.email}`)
    }

    message.success("Your account has been created.")
  }

  handleError = ({ data }) => {
    const { errors } = data.registerUser

    const { errorDefinitions } = this.state
    const {
      resource,
      field,
      code,
    } = errors[0]

    let errorMessage

    try {
      errorMessage = errorDefinitions[resource][field][code]
    } catch {
      errorMessage = "We could not process your request."
    }

    return {
      submitting: false,
      alert: {
        type: "error",
        message: "Malfunction.",
        description: <span>{errorMessage}</span>
      },
    }
  }

  render() {
    const { mutate } = this.props
    return (
      <section className="signup">
        <Helmet>
          <title>Sign Up - Metamapper</title>
          <script
            type="text/javascript"
            src="https://cdnjs.cloudflare.com/ajax/libs/zxcvbn/4.4.2/zxcvbn.js"
            secure
          />
        </Helmet>
        <Row>
          <Col span={8} offset={8}>
            <AuthForm
              title="Create an Account"
              mutate={mutate}
              component={SignupForm}
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

export default graphql(RegisterUser)(Signup)
