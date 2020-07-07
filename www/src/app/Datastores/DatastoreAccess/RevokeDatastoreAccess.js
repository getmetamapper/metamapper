import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Popconfirm } from "antd"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import GetDatastoreAccessPrivileges from "graphql/queries/GetDatastoreAccessPrivileges"
import UpdateDatastoreAccessPrivilegesMutation from "graphql/mutations/UpdateDatastoreAccessPrivileges"

class RevokeDatastoreAccess extends Component {
  handleRevoke = (evt) => {
    evt.preventDefault()

    const {
      datastore: { id },
      contentObject: { id: objectId },
    } = this.props

    const payload = {
      successMessage: "Changes have been saved.",
      variables: {
        id,
        objectId,
        privileges: [],
      },
      refetchQueries: [
        {
          query: GetDatastoreAccessPrivileges,
          variables: {
            datastoreId: id,
          },
        },
      ],
    }

    this.props.handleMutation(payload)
  }

  render() {
    return (
      <Popconfirm
        title="Are you sure?"
        onConfirm={this.handleRevoke}
        okText="Yes"
        cancelText="No"
      >
        {/* eslint-disable-next-line*/}
        <a role="button">
          Remove
        </a>
      </Popconfirm>
    )
  }
}

const enhance = compose(
  graphql(UpdateDatastoreAccessPrivilegesMutation),
  withGraphQLMutation
)

export default enhance(RevokeDatastoreAccess)
