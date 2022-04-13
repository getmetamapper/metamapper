import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { find } from "lodash"
import { withLargeLoader } from "hoc/withLoader"
import qs from "query-string"
import CheckExecutionDetails from "app/Datastores/DatastoreChecks/CheckExecution/CheckExecutionDetails"
import CheckExecutionsTable from "app/Datastores/DatastoreChecks/CheckExecutionsTable"
import withGetCheckExecutions from "graphql/withGetCheckExecutions"

class CheckExecutions extends Component {
  constructor(props) {
    super(props)

    this.state = {
      selectedExecution: props.selectedExecution,
      executionDetailsVisible: false,
    }
  }

  handleOpenDetails = (selectedExecution) => {
    const {
      location: { pathname },
    } = this.props

    this.setState({
      selectedExecution,
      executionDetailsVisible: true,
    })

    window.history.pushState(
      null,
      "",
      `${pathname}?selectedExecution=${selectedExecution.id}`
    )
  }

  handleCloseDetails = () => {
    const {
      location: { pathname },
    } = this.props

    this.setState({
      executionDetailsVisible: false,
    })

    window.history.pushState(null, "", pathname)
  }


  componentDidMount = () => {
    const {
      checkExecutions,
      location: { search },
    } = this.props

    const { selectedExecution } = qs.parse(search)
    const execution = find(checkExecutions, { id: selectedExecution })

    if (selectedExecution && execution) {
      this.handleOpenDetails(execution)
    }
  }

  render() {
    const {
      checkExpectations,
      checkExecutions,
      loading,
    } = this.props
    const {
      executionDetailsVisible,
      selectedExecution,
    } = this.state
    return (
      <div className="check-executions">
        <h2>
          Executions
        </h2>
        <CheckExecutionsTable
          checkExecutions={checkExecutions}
          loading={loading}
          onOpenDetails={this.handleOpenDetails}
        />
        <>
          {selectedExecution && (
            <CheckExecutionDetails
              checkExecution={selectedExecution}
              checkExpectations={checkExpectations}
              visible={executionDetailsVisible}
              onClose={this.handleCloseDetails}
              loading={loading}
            />
          )}
        </>
      </div>
    )
  }
}

export default compose(
  withRouter,
  withGetCheckExecutions,
  withLargeLoader,
)(CheckExecutions)
