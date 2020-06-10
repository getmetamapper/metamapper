import React, { Component } from "react"
import { Input, message } from "antd"
import { compose, graphql } from "react-apollo"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import EditableText from "app/Common/EditableText"
import UpdateDatastoreDescription from "graphql/mutations/UpdateDatastoreDescription"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreDescription extends Component {
  constructor(props) {
    super(props)

    this.state = {
      shortDesc: props.datastore.shortDesc,
      currentDesc: props.datastore.shortDesc,
    }

    this.resetContent = this.resetContent.bind(this)
  }

  handleChange = (e) => {
    this.setState({
      shortDesc: e.target.value,
    })
  }

  handleSave = (e) => {
    e.preventDefault()

    const {
      datastore: { id },
    } = this.props
    const { currentDesc, shortDesc } = this.state

    if (shortDesc && shortDesc.length > 140) {
      message.error('Datastore description cannot be longer than 140 characters.')
      this.resetContent()
      return;
    }

    const payload = {
      variables: {
        id,
        shortDesc,
      },
      successMessage: "Description was saved.",
    }

    if (currentDesc !== shortDesc) {
      this.props.handleMutation(payload, this.handleSubmitSuccess)
    }
  }

  resetContent = () => {
    this.setState({ shortDesc: this.state.currentDesc })
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.updateDatastoreMetadata

    if (errors && errors.length > 0) {
      this.resetContent()
    }
  }

  renderContent = (content, hasPermission) => {
    if (!content) {
      if (hasPermission) {
        return <i>Click here to enter a brief description.</i>
      }
      return <i>This datastore has no description.</i>
    }
    return <i>{content}</i>
  }

  render() {
    const { shortDesc } = this.state
    const {
      datastore: { tags },
      hasPermission,
    } = this.props
    return (
      <div
        data-test="DatastoreDescription"
        className={`datastore-description${
          tags.length <= 0 ? " mb-0" : " mb-20"
        }`}
      >
        <EditableText
          cypress="DatastoreDescription"
          content={this.renderContent(shortDesc, hasPermission)}
          disabled={!hasPermission}
          onClickButton={this.handleSave}
        >
          <Input
            value={shortDesc}
            onChange={this.handleChange}
            placeholder="Enter a brief description of the datastore"
            data-test="DatastoreDescription.Input"
          />
        </EditableText>
      </div>
    )
  }
}

export default compose(
  withWriteAccess,
  graphql(UpdateDatastoreDescription),
  withGraphQLMutation
)(DatastoreDescription)
