import React, { Component } from "react"
import { some, isEmpty } from "lodash"
import { Button, Card, Form, Icon, message, Steps } from "antd"
import Link from "app/Navigation/Link"
import SamlConnectionSetupConfigFieldset from "./SamlConnectionSetupConfigFieldset"
import SamlConnectionSetupDetails from "./SamlConnectionSetupDetails"
import SamlConnectionSetupMappingFieldset from "./SamlConnectionSetupMappingFieldset"

class SamlConnectionSetupForm extends Component {
  constructor(props) {
    super(props)
    this.state = {
      current: 0,
      configurationIsValid: false,
    }

    this.prev = this.prev.bind(this)
    this.next = this.next.bind(this)
  }

  checkFieldExistence = (fields) => {
    return !some(this.props.form.getFieldsValue(fields), isEmpty)
  }

  validateConnectionConfiguration = () => {
    const isValid = this.checkFieldExistence(["entityId", "ssoUrl", "x509cert"])

    if (!isValid) {
      message.error("Please fill out all the required fields.")
    } else {
      this.next()
    }
  }

  renderButton = (currentStep) => {
    if (currentStep === 0) {
      return (
        <Button type="primary" onClick={this.next}>
          Continue
        </Button>
      )
    }

    if (currentStep === 1) {
      return (
        <Button type="primary" onClick={this.validateConnectionConfiguration}>
          Continue
        </Button>
      )
    }
  }

  next() {
    this.setState({
      current: this.state.current + 1,
    })
  }

  prev() {
    this.setState({
      current: this.state.current - 1,
    })
  }

  render() {
    const { current } = this.state
    const {
      form,
      hasPermission,
      isEditing,
      isSubmitting,
      onSubmit,
      ssoConnection,
    } = this.props
    return (
      <Card>
        <Steps current={current}>
          <Steps.Step
            key={0}
            title="Configure IdP"
            icon={<Icon type="control" />}
          />
          <Steps.Step
            key={1}
            title="Configure Connection"
            icon={<Icon type="safety-certificate" />}
          />
          <Steps.Step
            key={2}
            title="Attribute Mapping"
            icon={<Icon type="api" />}
          />
        </Steps>
        <Form onSubmit={onSubmit} className="sso-connection-setup-form">
          <div className="steps-content">
            <div className={current === 0 ? "" : "hidden"}>
              <SamlConnectionSetupDetails ssoConnection={ssoConnection} />
            </div>
            <div className={current === 1 ? "" : "hidden"}>
              <SamlConnectionSetupConfigFieldset
                form={form}
                hasPermission={hasPermission}
                ssoConnection={ssoConnection}
              />
            </div>
            <div className={current === 2 ? "" : "hidden"}>
              <SamlConnectionSetupMappingFieldset
                form={form}
                ssoConnection={ssoConnection}
                hasPermission={hasPermission}
              />
            </div>
          </div>
          <div className="steps-action">
            <Link to="/settings/authentication">
              <Button type="default mr-10">Cancel</Button>
            </Link>
            {current > 0 && (
              <Button type="default" onClick={this.prev}>
                Previous
              </Button>
            )}
            <div className="pull-right">
              <>{this.renderButton(current)}</>
              <>
                <Button
                  type="primary"
                  htmlType="submit"
                  className={current === 2 ? "" : "hidden"}
                >
                  {isSubmitting
                    ? "Saving..."
                    : `${isEditing ? "Update" : "Create"} Connection`}
                </Button>
              </>
            </div>
          </div>
        </Form>
      </Card>
    )
  }
}

export default SamlConnectionSetupForm
