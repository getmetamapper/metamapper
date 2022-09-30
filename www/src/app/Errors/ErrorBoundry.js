import React, { Component } from "react"
import ServerError from "./ServerError"

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
    }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {

  }

  render() {
    const { hasError } = this.state
    const { children } = this.props

    if (hasError) {
      return <ServerError />
    }

    return children
  }
}

export default ErrorBoundary
