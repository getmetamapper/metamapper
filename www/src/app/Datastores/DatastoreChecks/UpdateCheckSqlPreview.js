import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Button } from "antd"
import PreviewCheckQueryMutation from "graphql/mutations/PreviewCheckQuery"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateCheckSqlPreview extends Component {
  handleSubmit = () => {
    const {
      datastore: { id: datastoreId },
      sqlText,
      interval,
    } = this.props

    if (!sqlText) {
      return;
    }

    const payload = {
      variables: {
        datastoreId,
        sqlText,
        interval,
      },
      successMessage: null,
    }

    this.props.handleMutation(payload, this.props.onSuccess)
  }

  render() {
    const { disabled, submitting } = this.props
    return (
      <Button type="primary" disabled={disabled || submitting} onClick={this.handleSubmit}>
        {submitting ? 'Running...' : 'Preview'}
      </Button>
    )
  }
}

export default compose(
  graphql(PreviewCheckQueryMutation),
  withGraphQLMutation,
)(UpdateCheckSqlPreview)
