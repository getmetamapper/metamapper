import React from "react"
import { Spin } from "antd"

const withLoader = (opts = {}) => (ChildComponent) => {
  const withInnerLoader = (props) => {
    if (props.loading) {
      const { wrapperClass, wrapperstyles } = opts

      return (
        <div className={wrapperClass} style={wrapperstyles}>
          <Spin {...opts} />
        </div>
      )
    }

    return <ChildComponent {...props} />
  }

  return withInnerLoader
}

export const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

export default withLoader
