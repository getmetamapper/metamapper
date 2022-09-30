import React, { Component, Fragment } from "react"
import { compose } from "react-apollo"
import { some, isEmpty } from "lodash"
import { withRouter } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import { Alert, Button, Col, Form, Icon, message, Row, Steps } from "antd"
import CheckFieldset from "app/Datastores/DatastoreChecks/CheckFieldset"
import CheckSetupSql from "app/Datastores/DatastoreChecks/CheckSetup/CheckSetupSql"
import CheckSetupExpectations from "app/Datastores/DatastoreChecks/CheckSetup/CheckSetupExpectations"
import UpdateCheckSqlPreview from "app/Datastores/DatastoreChecks/UpdateCheckSqlPreview"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetCheckIntervalOptions from "graphql/withGetCheckIntervalOptions"

class CheckSetupForm extends Component {
  constructor(props) {
    super(props)
    this.state = {
      current: 0,
      query: null,
      queryResults: null,
      sqlException: null,
      sqlIsRunning: false,
      sqlText: "",
    }

    this.handleSqlChange = this.handleSqlChange.bind(this)
  }

  checkFieldExistence = (fields) => {
    return !some(this.props.form.getFieldsValue(fields), isEmpty)
  }

  validateMetadata = () => {
    const isValid = this.checkFieldExistence(["name", "interval"])

    if (!isValid) {
      message.error("Please fill out all the required fields.")
    } else {
      this.next()
    }
  }

  validateExpectations = () => {
    this.next()
  }

  renderButton = (currentStep) => {
    const { form, datastore } = this.props

    if (currentStep === 0) {
      return (
        <Button
          type="primary"
          onClick={this.validateMetadata}
          data-test="CheckSetupForm.validateMetadata"
        >
          Continue
        </Button>
      )
    }

    const queryExists = this.checkFieldExistence(["queryId"])

    if (currentStep === 1 && queryExists) {
      return (
        <Button type="primary" onClick={() => this.next()} data-test="CheckSetupForm.VerifyConnection">
          Continue
        </Button>
      )
    }

    if (currentStep === 1 && !queryExists) {
      return (
        <UpdateCheckSqlPreview
          datastore={datastore}
          interval={form.getFieldValue("interval")}
          sqlText={this.state.sqlText}
          onSubmit={this.handlePreviewSubmit}
          onSuccess={this.handlePreviewSuccess}
        />
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

  handlePreviewSubmit = () => {
    this.setState({ sqlIsRunning: true, sqlException: null })
  }

  handlePreviewSuccess = ({ data: { previewCheckQuery } }) => {
    const {
      errors,
      query,
      queryResults,
      sqlException,
    } = previewCheckQuery

    this.setState({ sqlIsRunning: false })

    if (!errors && query) {
      this.props.form.setFieldsValue({ queryId: query.id })
      this.setState({ query, queryResults, sqlException: null })
    }

    if (sqlException) {
      this.setState({ sqlException, queryResults: [] })
    }
  }

  handleSqlChange = (e) => {
    this.setState({
      query: null,
      sqlText: e.target.value,
      sqlException: null,
    })

    this.props.form.setFieldsValue({ queryId: null })
  }

  render() {
    const {
      form,
      checkIntervalOptions,
      hasPermission,
      isSubmitting,
      onSubmit,
    } = this.props
    const { current, query, queryResults, sqlException, sqlIsRunning } = this.state
    return (
      <Fragment>
        <Row className="check-setup-form-navbar">
          <Col>
            <div className="steps-action">
              <div className="pull-left">
                <Button onClick={() => this.prev()} disabled={current === 0}>
                  Previous
                </Button>
              </div>
              <div className="pull-right">
                <>{this.renderButton(current)}</>
                <>
                  <Button
                    type="primary"
                    htmlType="submit"
                    className={current === 2 ? "" : "hidden"}
                    data-test="CheckSetupForm.Submit"
                    onClick={this.props.onSubmit}
                  >
                    {isSubmitting ? "Saving..." : "Create Check"}
                  </Button>
                </>
              </div>
            </div>
          </Col>
        </Row>
        <Row className="check-setup-form">
          <Col span={4}>
            <Steps current={current} direction="vertical">
              <Steps.Step
                key={0}
                title="Metadata"
                icon={<Icon type="info-circle" />}
              />
              <Steps.Step
                key={1}
                title="SQL"
                icon={<Icon type="code" />}
              />
              <Steps.Step
                key={2}
                title="Expectations"
                icon={<Icon type="check-square" />}
              />
            </Steps>
            <div className="steps-tooltip">
              <div className={current === 0 ? "metadata" : "hidden"}>
                <Alert
                  message="Configure the check."
                  description={
                    <span>
                      Checks are simple tests against data in your
                      datastore. Use them to measure data quality, detect
                      completeness of data, etc.
                    </span>
                  }
                />
              </div>
              <div className={current === 1 ? "sql" : "hidden"}>
                <Alert
                  message="Write some SQL."
                  description={
                    <span>
                      Pull a dataset from your datastore. We will define
                      a series of data quality tests to run against the
                      results in the next step.
                    </span>
                  }
                />
              </div>
              <div className={current === 2 ? "expectations" : "hidden"}>
                <Alert
                  message="Define your expectations."
                  description={
                    <span>
                      These are a series of tests that we will run
                      against the result of your SQL query. If any
                      of those tests do not pass, the check will fail.
                    </span>
                  }
                />
              </div>
            </div>
          </Col>
          <Col span={20}>
            <Form onSubmit={onSubmit}>
              <div className="steps-content">
                <div className={current === 0 ? "metadata" : "hidden"}>
                  <CheckFieldset
                    checkIntervalOptions={checkIntervalOptions}
                    form={form}
                    hasPermission={hasPermission}
                  />
                </div>
                <div className={current === 1 ? "sql" : "hidden"}>
                  <CheckSetupSql
                    form={form}
                    sqlText={this.state.sqlText}
                    sqlException={sqlException}
                    sqlIsRunning={sqlIsRunning}
                    queryResults={queryResults}
                    onChange={this.handleSqlChange}
                  />
                </div>
                <div className={current === 2 ? "expectations" : "hidden"}>
                  <CheckSetupExpectations
                    form={form}
                    hasPermission={hasPermission}
                    queryColumns={query && query.columns}
                  />
                </div>
              </div>
            </Form>
          </Col>
        </Row>
      </Fragment>
    )
  }
}

export default compose(
  withRouter,
  withGetDatastoreSettings,
  withGetCheckIntervalOptions,
  withLargeLoader,
)(CheckSetupForm)
