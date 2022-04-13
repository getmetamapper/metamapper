import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withUserContext } from "context/UserContext"
import { withRouter, Link, Prompt } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGetDatastoreDefinition from "graphql/withGetDatastoreDefinition"
import withGetColumnDefinition from "graphql/withGetColumnDefinition"
import PermissionDenied from "app/Errors/PermissionDenied"
import ReadmeEditor from "app/Datastores/Readme/ReadmeEditor"
import UpdateColumnReadmeMutation from "graphql/mutations/UpdateColumnReadme"

class DefinitionColumnReadmeEditor extends Component {
  constructor(props) {
    super(props)

    const {
      columnDefinition
    } = props

    this.state = {
      current: columnDefinition.readme,
      previous: columnDefinition.readme,
    }

    this.handleChange = this.handleChange.bind(this)
    this.handleClose = this.handleClose.bind(this)
  }

  handleSubmit = () => {
    const { current: readme } = this.state
    const {
      columnDefinition: { id }
    } = this.props

    const payload = {
      variables: {
        id,
        readme,
      },
      successMessage: "Changes have been saved.",
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.updateColumnMetadata

    if (!errors) {
      const { current } = this.state

      this.setState({
        previous: current,
      })
    }
  }

  getRedirectUrl = () => {
    const {
      match: {
        params: {
          datastoreSlug,
          schemaName,
          tableName,
        },
      },
      columnDefinition: { id },
      currentWorkspace: { slug },
    } = this.props
    return (
      `/${slug}/datastores/${datastoreSlug}/definition/${schemaName}/${tableName}/columns?selectedColumn=${id}`
    )
  }

  getTitle = () => {
    const {
      match: {
        params: {
          schemaName,
          tableName,
        },
      },
      columnDefinition: { name },
    } = this.props
    return (
      <>
        Currently editing: <Link to={this.getRedirectUrl()}>{schemaName}.{tableName}.{name}</Link>
      </>
    )
  }

  handleChange = (markdown) => {
    this.setState({ current: markdown })
  }

  handleClose = () => {
    this.props.history.push(this.getRedirectUrl())
  }

  render() {
    const {
      loading,
      submitting,
      hasPermission,
    } = this.props
    if (!hasPermission) {
      return <PermissionDenied to={this.getRedirectUrl()} />
    }
    return (
      <div className="definition-readme-editor">
        <Prompt
          message="You have unsaved changes. Are you sure you want to leave?"
          when={this.state.current !== this.state.previous}
        />
        <ReadmeEditor
          title={this.getTitle()}
          markdown={this.state.current}
          loading={loading}
          submitting={submitting}
          onSubmit={this.handleSubmit}
          onChange={this.handleChange}
          onClose={this.handleClose}
        />
      </div>
    )
  }
}

const withNotFound = withNotFoundHandler(({ columnDefinition }) => {
  return !columnDefinition || !columnDefinition.hasOwnProperty("id")
})

const enhance = compose(
  withRouter,
  withUserContext,
  withWriteAccess,
  withGetDatastoreDefinition,
  withGetColumnDefinition,
  graphql(UpdateColumnReadmeMutation),
  withGraphQLMutation,
  withLargeLoader,
  withNotFound,
)

export default enhance(DefinitionColumnReadmeEditor)
