import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { map, some, isEmpty } from "lodash"
import { withRouter } from "react-router-dom"
import {
  Avatar,
  Button,
  Card,
  Col,
  Divider,
  Form,
  Icon,
  message,
  Radio,
  Row,
  Steps,
} from "antd"
import { withLargeLoader } from "hoc/withLoader"
import Link from "app/Navigation/Link"
import RestrictedButton from "app/Common/RestrictedButton"
import DatastoreSettingsFieldset from "app/Datastores/DatastoreSettings/DatastoreSettingsFieldset"
import ConnectionSettingsFieldset from "app/Datastores/ConnectionSettings/ConnectionSettingsFieldset"
import TestJdbcConnection from "graphql/mutations/TestJdbcConnection"
import withGetDatastoreEngines from "graphql/withGetDatastoreEngines"
import withGetWorkspaceBySlug from "graphql/withGetWorkspaceBySlug"

class DatastoreSetupForm extends Component {
  constructor(props) {
    super(props)
    this.state = {
      current: 0,
      connectionIsValid: false,
      connectionIsTesting: false,
      connectionProperties: {},
    }
  }

  checkFieldExistence = (fields) => {
    return !some(this.props.form.getFieldsValue(fields), isEmpty)
  }

  validateEngine = () => {
    const isValid = this.checkFieldExistence(["engine"])

    if (!isValid) {
      message.error("Select a database engine to continue.")
    } else {
      this.next()
    }
  }

  validateConnectionSettings = () => {
    const isValid = this.checkFieldExistence([
      "host",
      "username",
      "password",
      "port",
      "database",
    ])

    if (!isValid) {
      message.error("Please fill out all the required fields.")
    }

    return isValid
  }

  testConnection = () => {
    const isValid = this.validateConnectionSettings()

    const variables = this.props.form.getFieldsValue([
      "engine",
      "host",
      "username",
      "password",
      "port",
      "database",
      "extras",
      "sshEnabled",
      "sshHost",
      "sshUser",
      "sshPort",
    ])

    if (variables.engine === "bigquery") {
      variables.extras.credentials = JSON.parse(variables.extras.credentials)
    }

    if (isValid) {
      this.setState({ connectionIsTesting: true })

      const httpRequest = this.props.mutate({ variables })
      const that = this

      httpRequest
        .then((response) => {
          setTimeout(() => that.handleTestConnection(variables, response), 1000)
        })
        .catch((err) => {
          setTimeout(() => that.handleTestConnectionFailure(err.graphQLErrors), 1000)
        })
    }
  }

  handleTestConnection = (
    connectionProperties,
    { data: { testJdbcConnection } }
  ) => {
    const connectionIsValid = testJdbcConnection.ok

    if (!connectionIsValid) {
      message.error("Could not connect to datastore with these credentials.")
    }

    this.setState({
      connectionIsValid,
      connectionProperties,
      connectionIsTesting: false,
    })
  }

  handleTestConnectionFailure = (errors) => {
    if (errors && errors.length > 0) {
      message.error(errors[0].message)
    }

    this.setState({ connectionIsTesting: false })
  }

  renderButton = (currentStep) => {
    if (currentStep === 0) {
      const { hasPermission } = this.props
      return (
        <RestrictedButton
          type="primary"
          onClick={this.validateEngine}
          hasPermission={hasPermission}
          data-test="DatastoreSetupForm.ValidateEngine"
        >
          Continue
        </RestrictedButton>
      )
    }

    const { connectionIsValid, connectionIsTesting } = this.state

    if (currentStep === 1 && connectionIsValid) {
      return (
        <Button type="primary" onClick={() => this.next()} data-test="DatastoreSetupForm.VerifyConnection">
          Continue
        </Button>
      )
    }

    if (currentStep === 1 && !connectionIsValid) {
      return (
        <Button
          type="default"
          onClick={this.testConnection}
          disabled={connectionIsTesting}
          data-test="DatastoreSetupForm.TestConnection"
        >
          {connectionIsTesting ? "Testing..." : "Test Connection"}
        </Button>
      )
    }
  }

  handleConnectionChange = () => {
    this.setState({
      connectionIsValid: false,
    })
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
      datastoreEngines,
      form,
      hasPermission,
      workspace,
      isSubmitting,
      onSubmit,
    } = this.props
    return (
      <Card>
        <h3 className="text-centered mb-0">
          <div>Connect a New Datastore</div>
          <small>
            <Link to="/datastores">(nevermind)</Link>
          </small>
        </h3>
        <Divider />
        <Row>
          <Col span={6}>
            <Steps current={current} direction="vertical">
              <Steps.Step
                key={0}
                title="Engine"
                icon={<Icon type="database" />}
              />
              <Steps.Step
                key={1}
                title="Credentials"
                icon={<Icon type="unlock" />}
              />
              <Steps.Step
                key={2}
                title="Metadata"
                icon={<Icon type="info-circle" />}
              />
            </Steps>
          </Col>
          <Col span={18}>
            <Form onSubmit={onSubmit} className="datastore-setup-form">
              <div className="steps-content">
                <div className={current === 0 ? "" : "hidden"}>
                  <h3>Select a datastore engine</h3>
                  <p>
                    We currently support connections to the engines listed
                    below.
                  </p>
                  {form.getFieldDecorator(
                    "engine",
                    {}
                  )(
                    <Radio.Group size="large" className="radio-icon">
                      {map(datastoreEngines || [], ({ label, dialect }) => (
                        <Radio.Button value={dialect} key={dialect}>
                          <Avatar
                            shape="square"
                            src={`/assets/static/img/datastores/dialects/${dialect}.png`}
                          />
                          <span className="text">{label}</span>
                        </Radio.Button>
                      ))}
                    </Radio.Group>
                  )}
                </div>
                <div className={current === 1 ? "" : "hidden"}>
                  <h3>
                    <span>Provide your credentials</span>
                    <span className="datastore-credentials-icon">
                      <Avatar
                        shape="square"
                        src={`/assets/static/img/datastores/dialects/${form.getFieldValue("engine")}.png`}
                      />
                    </span>
                  </h3>
                  <p>
                    Please enter the credentials from your database provider
                    into the form below. The username and password must have
                    read access to the database.
                  </p>
                  <ConnectionSettingsFieldset
                    engine={form.getFieldValue("engine")}
                    publicKey={workspace ? workspace.sshPublicKey : null}
                    form={form}
                    onChange={this.handleConnectionChange}
                    hasPermission={hasPermission}
                  />
                </div>
                <div className={current === 2 ? "" : "hidden"}>
                  <DatastoreSettingsFieldset
                    form={form}
                    hasPermission={hasPermission}
                  />
                </div>
              </div>
              <div className="steps-action">
                {current > 0 && (
                  <Button onClick={() => this.prev()}>Previous</Button>
                )}
                <div className="pull-right">
                  <>{this.renderButton(current)}</>
                  <>
                    <Button
                      type="primary"
                      htmlType="submit"
                      className={current === 2 ? "" : "hidden"}
                      data-test="DatastoreSetupForm.Submit"
                    >
                      {isSubmitting ? "Saving..." : "Create Datastore"}
                    </Button>
                  </>
                </div>
              </div>
            </Form>
          </Col>
        </Row>
      </Card>
    )
  }
}

export default compose(
  withRouter,
  withGetWorkspaceBySlug,
  withGetDatastoreEngines,
  withLargeLoader,
  graphql(TestJdbcConnection)
)(DatastoreSetupForm)
