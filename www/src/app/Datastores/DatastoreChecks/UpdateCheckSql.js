import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Button } from "antd"
import UpdateCheckQueryMutation from "graphql/mutations/UpdateCheckQuery"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class UpdateCheckSql extends Component {
  handleSubmit = () => {
    const { check, query } = this.props

    if (!check || !check.hasOwnProperty("id")) {
      return;
    }

    if (!query || !query.hasOwnProperty("id")) {
      return;
    }

    const payload = {
      variables: {
        id: check.id,
        queryId: query.id,
      },
      successMessage: null,
    }

    this.props.handleMutation(payload, this.props.onSuccess)
  }

  render() {
    const { disabled, submitting } = this.props
    return (
      <Button type="primary" disabled={submitting || disabled} onClick={this.handleSubmit}>
        {submitting ? 'Saving...' : 'Save Changes'}
      </Button>
    )
  }
}

export default compose(
  graphql(UpdateCheckQueryMutation),
  withGraphQLMutation,
)(UpdateCheckSql)
