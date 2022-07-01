import React from "react"
import { Link } from "react-router-dom"
import { Result, Button, Icon } from "antd"

const ServerError = () => (
  <Result
    title="500"
    icon={<Icon type="frown" />}
    subTitle="Uh, oh! Something went wrong."
    extra={
      <Link to="/">
        <Button type="primary">Go Back Home</Button>
      </Link>
    }
  />
)

export default ServerError
