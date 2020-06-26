import React, { Component, Fragment } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Divider, Row, message } from "antd"
import { getErrorDefinition, setToken } from "lib/utilities"
import yaml from "js-yaml"
import AuthForm from "app/Authentication/AuthForm"
import AccountSetupForm from "app/Authentication/AccountSetupForm"
import AccountSetupMutation from "graphql/mutations/AccountSetup"

class AccountSetup extends Component {
  state = { errorDefinition: {} }

  constructor(props) {
    super(props)

    getErrorDefinition('en').then(txt => {
      const {
        errors: errorDefinitions,
      } = yaml.safeLoad(txt)

      this.setState({ errorDefinitions })
    })
  }

  handleSuccess = ({ data }) => {
    const { jwt, errors } = data.accountSetup

    if (errors && errors.length > 0) {
      return this.handleError({ data })
    }

    if (jwt) {
      setToken(jwt)

      this.props.refreshUser()
      this.props.history.push(`/`)
    }
  }

  handleError = ({ data }) => {
    const { errors } = data.accountSetup

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
      <section className="account-setup">
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
              title="Welcome to Metamapper!"
              description={
                <Fragment>
                  <p className="text-centered">
                    Before you can continue, you will need to do a quick setup.
                  </p>
                  <Divider />
                </Fragment>
              }
              mutate={mutate}
              component={AccountSetupForm}
              onSuccess={this.handleSuccess}
              onError={this.handleError}
              links={[]}
            />
          </Col>
        </Row>
      </section>
    )
  }
}

export default graphql(AccountSetupMutation)(AccountSetup)
