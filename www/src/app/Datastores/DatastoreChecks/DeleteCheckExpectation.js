import React, { Component } from "react"
import PropTypes from "prop-types"
import { compose, graphql } from "react-apollo"
import { Popconfirm } from "antd"
import DeleteCheckExpectationMutation from "graphql/mutations/DeleteCheckExpectation"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DeleteCheckExpectation extends Component {
  constructor(props) {
    super(props)

    this.handleDeletion = this.handleDeletion.bind(this)
  }

  handleDeletion(evt) {
    evt.preventDefault()

    const { expectationId } = this.props
    const payload = {
      successMessage: null,
      variables: { id: expectationId },
      refetchQueries: ["GetCheckExpectations"],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    if (this.props.onSubmit) {
      this.props.onSubmit()
    }
  }

  render() {
    return (
      <Popconfirm
        title="Are you sure?"
        onConfirm={this.handleDeletion}
        okText="Yes"
        cancelText="No"
        data-test="DeleteCheckExecution.Confirm"
      >
        {/* eslint-disable-next-line */}
        <a role="button" data-test="DeleteCheckExecution.Submit">
          remove
        </a>
      </Popconfirm>
    )
  }
}

DeleteCheckExpectation.propTypes = {
  expectationId: PropTypes.string.isRequired,
}

export default compose(
  graphql(DeleteCheckExpectationMutation),
  withGraphQLMutation,
)(DeleteCheckExpectation)
