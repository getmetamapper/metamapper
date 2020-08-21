import React, { Component } from "react"
import { Input, message } from "antd"
import { compose, graphql } from "react-apollo"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import EditableText from "app/Common/EditableText"
import UpdateTableMetadata from "graphql/mutations/UpdateTableMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class TableDescription extends Component {
  constructor(props) {
    super(props)

    this.state = {
      shortDesc: props.table.shortDesc,
      currentDesc: props.table.shortDesc,
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
      table: { id },
    } = this.props
    const { currentDesc, shortDesc } = this.state

    if (shortDesc && shortDesc.length > 140) {
      message.error('Table description cannot be longer than 140 characters.')
      this.setState({ shortDesc: currentDesc })
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

  handleSubmitSuccess = ({ data }) => {
    const { table, errors } = data.updateTableMetadata

    if (errors && errors.length > 0) {
      this.resetContent()
    } else {
      this.setState({ shortDesc: table.shortDesc })
    }
  }

  resetContent = () => {
    this.setState({ shortDesc: this.state.currentDesc })
  }

  renderContent = (content, hasPermission) => {
    if (!content) {
      if (hasPermission) {
        return <i>Click here to enter a brief description.</i>
      }
      return <i>This table has no description.</i>
    }
    return <i>{content}</i>
  }

  render() {
    const { shortDesc } = this.state
    const { hasPermission } = this.props
    return (
      <div data-test="TableDescription" className="table-description">
        <EditableText
          cypress="TableDescription"
          content={this.renderContent(shortDesc, hasPermission)}
          disabled={!hasPermission}
          onClickButton={this.handleSave}
        >
          <Input
            value={shortDesc}
            onChange={this.handleChange}
            placeholder="Enter a brief description of the table"
            data-test="TableDescription.Input"
          />
        </EditableText>
      </div>
    )
  }
}

export default compose(
  withWriteAccess,
  graphql(UpdateTableMetadata),
  withGraphQLMutation
)(TableDescription)
