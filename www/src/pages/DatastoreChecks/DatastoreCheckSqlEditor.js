import React, { Component } from "react"
import { compose } from "react-apollo"
import { message } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withRouter, Prompt } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import { ellipsis } from "lib/utilities"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import CodeEditor from "app/Common/CodeEditor"
import CheckSqlPreviewResults from "app/Datastores/DatastoreChecks/CheckSqlPreviewResults"
import UpdateCheckSqlPreview from "app/Datastores/DatastoreChecks/UpdateCheckSqlPreview"
import UpdateCheckSql from "app/Datastores/DatastoreChecks/UpdateCheckSql"
import withNotFoundHandler from "hoc/withNotFoundHandler"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withGetDatastoreCheck from "graphql/withGetDatastoreCheck"
import PermissionDenied from "app/Errors/PermissionDenied"

class DatastoreCheckSqlEditor extends Component {
  constructor(props) {
    super(props);

    const { check } = props

    this.state = {
      current: check.query.sqlText,
      previous: check.query.sqlText,
      queryResults: null,
      query: null,
      sqlException: null,
    }

    this.breadcrumbs = this.breadcrumbs.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      check,
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    return [
      {
        label: "Datastores",
        to: `/${slug}/datastores`,
      },
      {
        label: datastoreSlug,
        to: `/${slug}/datastores/${datastoreSlug}`,
      },
      {
        label: "Checks",
        to: `/${slug}/datastores/${datastoreSlug}/checks`,
      },
      {
        label: ellipsis(check.name),
        to: `/${slug}/datastores/${datastoreSlug}/checks/${check.pk}`,
      },
      {
        label: 'SQL',
      }
    ]
  }

  handlePreviewSuccess = ({ data: { previewCheckQuery } }) => {
    const {
      errors,
      query,
      queryResults,
      sqlException,
    } = previewCheckQuery

    if (!errors) {
      const { current } = this.state

      this.setState({
        previous: current,
        queryResults,
        query,
        sqlException,
      })
    }
  }

  handleUpdateSuccess = ({ data: { updateCheck } }) => {
    const { errors } = updateCheck
    const { history } = this.props

    if (!errors) {
      message.success('Query has been updated.')
      history.push(this.getRedirectUrl())
    }
  }

  handleChange = (e) => {
    this.setState({ current: e.target.value, query: null })
  }

  getRedirectUrl = () => {
    const {
      match: {
        params: {
          datastoreSlug,
          checkId,
        },
      },
      currentWorkspace: { slug },
    } = this.props
    return (
      `/${slug}/datastores/${datastoreSlug}/checks/${checkId}`
    )
  }

  render() {
    const {
      check,
      datastore,
      loading,
      hasPermission,
    } = this.props
    if (!hasPermission) {
      return <PermissionDenied to={this.getRedirectUrl()} />
    }
    const { queryResults, query, sqlException } = this.state
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`${check.name} - Checks - ${datastore.slug} - Metamapper`}
        hideSchemaSelector
      >
        <div className="check-sql-editor">
          <Prompt
            message="You have unsaved changes. Are you sure you want to leave?"
            when={this.state.current !== this.state.previous}
          />
          <div className="check-sql-editor-navbar">
            <UpdateCheckSqlPreview
              datastore={datastore}
              sqlText={this.state.current}
              interval={check.interval.value}
              disabled={(query && query.hasOwnProperty("id"))}
              onSuccess={this.handlePreviewSuccess}
            />
            <UpdateCheckSql
              check={check}
              query={query}
              disabled={(!query || !query.hasOwnProperty("id"))}
              onSuccess={this.handleUpdateSuccess}
            />
          </div>
          <CodeEditor
            mode="sql"
            value={this.state.current}
            onChange={this.handleChange}
          />
          <CheckSqlPreviewResults
            queryResults={queryResults}
            sqlException={sqlException}
          />
        </div>
      </DatastoreLayout>
    )
  }
}

const withNotFound = withNotFoundHandler(({ check, datastore }) => {
  return !datastore || !check || !datastore.hasOwnProperty("id") || !check.hasOwnProperty("id")
})

export default compose(
  withRouter,
  withWriteAccess,
  withGetDatastoreSettings,
  withGetDatastoreCheck,
  withLargeLoader,
  withNotFound,
)(DatastoreCheckSqlEditor)
