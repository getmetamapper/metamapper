import React, { Component, Fragment } from "react"
import { compose, graphql } from "react-apollo"
import { Button, Table } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import Markdown from "react-markdown"
import GetCheckExpectations from "graphql/queries/GetCheckExpectations"
import DeleteCheckExpectation from "app/Datastores/DatastoreChecks/DeleteCheckExpectation"
import CreateCheckExpectationMutation from "graphql/mutations/CreateCheckExpectation"
import CheckSetupExpectationForm from "app/Datastores/DatastoreChecks/CheckSetup/CheckSetupExpectationForm"
import withGetCheckHandlerOptions from "graphql/withGetCheckHandlerOptions"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class CheckExpectations extends Component {
  constructor(props) {
    super(props);

    this.state = {
      visible: false,
    }

    this.columns = [
      {
        title: "Description",
        dataIndex: "description",
        key: "description",
        render: description => <Markdown>{description}</Markdown>
      },
    ]

    if (props.hasPermission) {
      this.columns.push({
        align: "right",
        render: (record) => <DeleteCheckExpectation expectationId={record.id} />
      })
    }
  }

  handleOpen = () => this.setState({ visible: true })

  handleClose = () => this.setState({ visible: false })

  handleSubmit = (variables, onComplete) => {
    const { check: { id: checkId } } = this.props
    const payload = {
      variables: {
        id: checkId,
        ...variables,
      },
      refetchQueries: [
        {
          query: GetCheckExpectations,
          variables: { checkId },
        }
      ],
      successMessage: "Expectation was added.",
    }

    this.props.handleMutation(payload, (r) => this.handleSubmitSuccess(r, onComplete))
  }

  handleSubmitSuccess = ({ data: { createCheckExpectation } }, onComplete) => {
    const { errors } = createCheckExpectation

    if (!errors) {
      onComplete()
    }
  }

  render() {
    const {
      visible,
    } = this.state
    const {
      expectations,
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
        <div className="check-expectations">
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
      </Fragment>
    )
  }
}

export default compose(
  withGetCheckHandlerOptions,
  withLargeLoader,
  withWriteAccess,
  graphql(CreateCheckExpectationMutation),
  withGraphQLMutation,
)(CheckExpectations)
