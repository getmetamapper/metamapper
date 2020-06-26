import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { withLargeLoader } from "hoc/withLoader"
import withGetOpensourceSetupStatus from "graphql/withGetOpensourceSetupStatus"

export default (ChildComponent, ignoreRedirects = false) => {
  class ComposedComponent extends Component {
    // Our component just got rendered
    componentDidMount() {
      if (!ignoreRedirects) {
        this.shouldNavigateAway()
      }
    }

    // Our component just got updated
    componentDidUpdate() {
      if (!ignoreRedirects) {
        this.shouldNavigateAway()
      }
    }

    shouldNavigateAway() {
      const { initiateSetupProcess } = this.props

      if (initiateSetupProcess) {
        this.props.history.push('/account/setup')
      }
    }

    render() {
      return <ChildComponent {...this.props} />
    }
  }
  return compose(
    withRouter,
    withGetOpensourceSetupStatus,
    withLargeLoader,
  )(ComposedComponent)
}
