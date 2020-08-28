import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { graphql } from "react-apollo"
import { Col, Row, message } from "antd"
import qs from "query-string"
import TriggerSingleSignOn from "graphql/mutations/TriggerSingleSignOn"
import AuthForm from "app/Authentication/AuthForm"
import SingleSignOnForm from "app/Authentication/SingleSignOnForm"

class SingleSignOn extends Component {
  constructor(props) {
    super(props)

    this.links = [
      {
        to: "/login",
        prompt: "Already have an account?",
        text: "Sign in.",
      },
    ]
  }

  handleSuccess = ({ data }) => {
    const {
      redirectUrl,
    } = data.triggerSingleSignOn

    const { next } = qs.parse(this.props.location.search)

    let nextParam = ''
    if (next) {
      nextParam = `?next=${encodeURIComponent(next)}`
    }

    if (redirectUrl) {
      window.location.href = `${redirectUrl}${nextParam}`
    } else {
      message.error(
        "Workspace does not exist or does not have Single Sign-On enabled."
      )
    }
  }

  render() {
    const { mutate } = this.props
    return (
      <section className="single-sign-on">
        <Helmet>
          <title>Single Sign-On - Metamapper</title>
        </Helmet>
        <Row>
          <Col span={8} offset={8}>
            <AuthForm
              title="Single Sign-On"
              mutate={mutate}
              component={SingleSignOnForm}
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

export default graphql(TriggerSingleSignOn)(SingleSignOn)
