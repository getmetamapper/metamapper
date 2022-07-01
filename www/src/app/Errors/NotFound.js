import React from "react"
import { Link } from "react-router-dom"
import { Result, Button } from "antd"

const NotFound = () => (
  <Result
    title="404"
    subTitle="Sorry, the page you are looking for doesn't exist."
    extra={
      <Link to="/">
        <Button type="primary">Go Back Home</Button>
      </Link>
    }
  />
)

export default NotFound
