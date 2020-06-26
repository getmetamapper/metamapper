import React from "react"
import yaml from "js-yaml"
import { message } from "antd"
import { findKey } from "lodash"
import { getErrorDefinition } from "lib/utilities"

const withGraphQLMutation = (WrappedComponent) => {
  return class extends React.Component {
    state = {
      submitting: false,
      errorDefinitions: {},
    }

    constructor(props) {
      super(props)

      getErrorDefinition('en').then(txt => {
        const {
          errors: errorDefinitions,
        } = yaml.safeLoad(txt)

        this.setState({ errorDefinitions })
      })

      this.handleMutation = this.handleMutation.bind(this)
      this.handleSuccess = this.handleSuccess.bind(this)
      this.handleFailure = this.handleFailure.bind(this)
    }

    handleMutation(
      { variables, refetchQueries, successMessage, timeout = 500 },
      callback = null,
      mutation = "mutate"
    ) {
      this.setState({ submitting: true })

      setTimeout(() => {
        const response = this.props[mutation]({ variables, refetchQueries })

        response.then(({ data }) => {
          this.handleSuccess(data, successMessage)
        })

        response.catch(this.handleFailure)

        if (callback && typeof callback === "function") {
          response.then(callback)
        }
      }, timeout)
    }

    handleSuccess = (data, successMessage) => {
      const hasErrors = findKey(data, (o) => o.errors !== null)

      if (hasErrors) {
        const { errorDefinitions } = this.state
        const { errors } = data[hasErrors]
        const {
          resource,
          field,
          code,
        } = errors[0]

        let errorMessage
        try {
          errorMessage = errorDefinitions[resource][field][code]
        } catch {
          errorMessage = "We could not process your request."
        }

        message.error(errorMessage)
      } else if (successMessage) {
        message.success(successMessage)
      }

      this.setState({ submitting: false })
    }

    handleFailure = ({ networkError }) => {
      let errorMessage = "We could not process your request."

      if (networkError && networkError.statusCode === 403) {
        errorMessage = "You do not have permission to perform this action."
      }

      message.error(errorMessage)
      this.setState({ submitting: false })
    }

    render() {
      const { submitting } = this.state

      return (
        <WrappedComponent
          handleMutation={this.handleMutation}
          submitting={submitting}
          {...this.props}
        />
      )
    }
  }
}

export default withGraphQLMutation
