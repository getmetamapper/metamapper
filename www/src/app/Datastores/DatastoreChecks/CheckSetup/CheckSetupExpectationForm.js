import React, { Component, Fragment } from "react"
import { map, some, isEmpty } from "lodash"
import { Alert, Button, Drawer, Form, Radio, Steps } from "antd"
import CheckSetupExpectationFieldset from "./CheckSetupExpectationFieldset"
import CheckSetupPassValueFieldset from "./CheckSetupPassValueFieldset"

const defaultDrawerProps = {
  className: "expectation-setup-form",
  placement: "right",
  title: "Add New Expectation",
  width: 600,
}

class CheckSetupExpectationForm extends Component {
  constructor(props) {
    super(props);

    this.state = {
      current: 0,
    }
  }

  checkFieldExistence = (fields) => {
    return !some(this.props.form.getFieldsValue(fields), isEmpty)
  }

  renderButton = (currentStep) => {
    const { isSubmitting } = this.props

    if (currentStep === 0) {
      return (
        <Button
          type="primary"
          disabled={!this.checkFieldExistence(["handlerClass"])}
          onClick={() => this.next()}
        >
          Continue
        </Button>
      )
    }

    const isReady = !this.checkFieldExistence([
      "handlerClass",
      "handlerInput",
      "passValueClass",
      "passValueInput",
    ])

    return (
      <Button
        type="primary"
        disabled={isSubmitting || isReady}
        onClick={this.handleSubmit}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    )
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

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      this.props.onSubmit(variables, this.handleClose)
    })
  }

  handleClose = () => {
    this.props.onClose()
    this.props.form.resetFields()
    this.setState({
      current: 0,
      expectationHandler: null,
      passValueHandler: null,
    })
  }

  setExpectationHandler = (expectationHandler) => this.setState({ expectationHandler })

  setPassValueHandler = (passValueHandler) => this.setState({ passValueHandler })

  render() {
    const {
      current,
      expectationHandler,
      passValueHandler,
    } = this.state
    const {
      form,
      expectationHandlers,
      passValueHandlers,
      queryColumns,
      visible,
    } = this.props
    return (
      <Drawer
        visible={visible}
        onClose={this.handleClose}
        {...defaultDrawerProps}
      >
        <div className="steps-navigation">
          <Steps current={current}>
            <Steps.Step key={0} onClick={() => current === 1 && this.prev()} />
            <Steps.Step key={1} />
          </Steps>
        </div>
        <div className="steps-content">
          <div className={current === 0 ? "expectation" : "hidden"}>
            <Alert
              message="Choose an expectation"
              description="We will periodically run this test against the results of your SQL query."
              type="info"
              showIcon
            />
            {form.getFieldDecorator(
              "handlerClass",
              {
                rules: [{ required: true, message: "This field is required." }],
              }
            )(
              <Radio.Group className="check-expectation-options">
                {map(expectationHandlers, (option) => (
                  <Radio.Button
                    key={option.handler}
                    value={option.handler}
                    onClick={() => this.setExpectationHandler(option)}
                  >
                    <Fragment>
                      <p className="name">{option.name}</p>
                      <p className="info">{option.info}</p>
                    </Fragment>
                  </Radio.Button>
                ))}
              </Radio.Group>
            )}
          </div>
          <div className={current === 1 ? "conditions" : "hidden"}>
            <Alert
              message="Set conditions"
              description="Define the parameters for your test."
              type="info"
              showIcon
            />
            {expectationHandler && (
              <Fragment>
                <CheckSetupExpectationFieldset
                  form={form}
                  queryColumns={queryColumns}
                  handler={expectationHandler}
                />
                <CheckSetupPassValueFieldset
                  form={form}
                  queryColumns={queryColumns}
                  handler={passValueHandler}
                  handlerOptions={passValueHandlers}
                  onSelect={this.setPassValueHandler}
                />
              </Fragment>
            )}
          </div>
        </div>
        <div className="steps-footer">
          <div className="pull-left">
            <Button onClick={() => this.prev()} disabled={current === 0}>
              Previous
            </Button>
          </div>
          <div className="pull-right">
            {this.renderButton(current)}
          </div>
        </div>
      </Drawer>
    )
  }
}

export default Form.create()(CheckSetupExpectationForm)
