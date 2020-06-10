import React from "react"
import { Alert } from "antd"

const AuthMessage = (props) => {
  const { type, message, ...rest } = props

  if (!message) {
    return null
  }

  return <Alert type={type} message={message} {...rest} />
}

export default AuthMessage
