import React from "react"
import { Link } from "react-router-dom"
import { Form, Icon } from "antd"
import { b64decode } from "lib/utilities"
import { AUTH_TOKEN } from "lib/constants"
import { withUserContext } from "context/UserContext"
import qs from "query-string"
import AuthMessage from "./AuthMessage"

class AuthForm extends React.Component {
  constructor(props) {
    super(props)

    const { error } = qs.parse(window.location.search)

    let type = ""
    let message = ""
    const description = b64decode(error)

    if (description.length > 0) {
      type = "error"
      message = "There was an error."
    }

    this.state = {
      alert: {
        type,
        message,
        description,
      },
      submitting: false,
    }
  }

  static defaultProps = {
    timeout: 1000,
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    window.localStorage.removeItem(AUTH_TOKEN)

    this.props.form.validateFields((err, variables) => {
      if (err) return

      this.setState({ submitting: true })

      setTimeout(() => {
        this.props
          .mutate({ variables })
          .then(this.handleSuccess)
          .catch(this.handleError)
      }, this.props.timeout)
    })
  }

  handleSuccess = (payload) => {
    let props = {}
    if (this.props.onSuccess) {
      props = this.props.onSuccess(payload)
    }

    this.setState({ submitting: false, ...props })
  }

  handleError = (e) => {
    let state = { submitting: false }

    if (this.props.onError) {
      state = { ...state, ...this.props.onError(e) }
    }

    this.setState(state)
  }

  render() {
    const { component: Component, title, description, form, links } = this.props
    const { alert, submitting } = this.state
    return (
      <div className="auth-form">
        <div className="logo">
          <img src="/assets/static/img/brand/icon.png" alt="Metamapper" />
        </div>
        <h2>{title}</h2>
        {description}
        <div className="auth-message">
          <AuthMessage
            showIcon
            icon={<Icon type={alert.type === "error" ? "frown" : "smile"} />}
            {...alert}
          />
        </div>
        <Component
          form={form}
          onSubmit={this.handleSubmit}
          submitting={submitting}
        />
        {links && links.length > 0 ? (
          <div className="auth-links">
            {links.map((link) => (
              <p key={link.to}>
                {link.prompt} <Link to={link.to}>{link.text}</Link>
              </p>
            ))}
          </div>
        ) : null}
      </div>
    )
  }
}

export default withUserContext(Form.create()(AuthForm))
