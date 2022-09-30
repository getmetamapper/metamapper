import React, { Component, Fragment } from "react"
import { compose, graphql } from "react-apollo"
import { Button, Table, Input } from "antd"
import { concat, pullAt, pick, map } from "lodash"
import { withLargeLoader } from "hoc/withLoader"
import Markdown from "react-markdown"
import PreviewCheckExpectationMutation from "graphql/mutations/PreviewCheckExpectation"
import CheckSetupExpectationForm from "app/Datastores/DatastoreChecks/CheckSetup/CheckSetupExpectationForm"
import withGetCheckHandlerOptions from "graphql/withGetCheckHandlerOptions"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class CheckSetupExpectations extends Component {
  constructor(props) {
    super(props);

    this.state = {
      expectations: [],
      visible: false,
    }

    this.columns = [
      {
        dataIndex: "description",
        key: "description",
        title: "Description",
        render: description => <Markdown>{description}</Markdown>
      },
      {
        align: "right",
        render: (item, record, index) => (
          <>
            {/* eslint-disable-next-line*/}
            <a role="button" onClick={() => this.handleRemove(index)}>
              remove
            </a>
          </>
        )
      }
    ]
  }

  handleOpen = () => {
    this.setState({ visible: true })
  }

  handleClose = () => {
    this.setState({ visible: false })
  }

  handleRemove = (index) => {
    const { expectations } = this.state

    if (index > -1) {
      pullAt(expectations, [index])
    }

    this.setState({ expectations })
  }

  handleSubmit = (variables, onComplete) => {
    const payload = {
      variables,
      successMessage: "Expectation was added.",
    }

    this.props.handleMutation(payload, (r) => this.handleSubmitSuccess(r, onComplete))
  }

  handleSubmitSuccess = ({ data: { previewCheckExpectation } }, onComplete) => {
    const { errors, expectation } = previewCheckExpectation

    if (!errors) {
      const expectations = concat(this.state.expectations, expectation)

      this.setState({ expectations } )
      this.props.form.setFieldsValue({
        expectations: map(expectations, r => pick(r, ['handlerClass', 'handlerInput', 'passValueClass', 'passValueInput']))
      })

      onComplete()
    }
  }

  render() {
    const {
      expectations,
      visible,
    } = this.state
    const {
      form,
      expectationHandlers,
      passValueHandlers,
      queryColumns,
      submitting,
    } = this.props
    return (
      <Fragment>
        <Button type="primary" onClick={this.handleOpen}>
          Add Expectation
        </Button>
        <div className="check-setup-expectations">
          <Table
            dataSource={expectations}
            pagination={false}
            columns={this.columns}
            locale={{ emptyText: "No expectations found." }}
          />
        </div>
        <CheckSetupExpectationForm
          expectationHandlers={expectationHandlers}
          passValueHandlers={passValueHandlers}
          queryColumns={queryColumns}
          visible={visible}
          onClose={this.handleClose}
          isSubmitting={submitting}
          onSubmit={this.handleSubmit}
        />
        {form.getFieldDecorator(
          "expectations",
          {}
        )(
          <Input type="hidden" />
        )}
      </Fragment>
    )
  }
}

export default compose(
  withGetCheckHandlerOptions,
  withLargeLoader,
  graphql(PreviewCheckExpectationMutation),
  withGraphQLMutation,
)(CheckSetupExpectations)
