import React from "react"
import NotFound from "app/Errors/NotFound"

export default (callable) => (ChildComponent) => {
  const withNotFoundHandler = (props) => {
    if (callable(props)) {
      return <NotFound />
    }
    return <ChildComponent {...props} />
  }
  return withNotFoundHandler
}
