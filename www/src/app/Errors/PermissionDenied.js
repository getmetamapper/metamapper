import React from 'react'
import { Link } from 'react-router-dom'
import { Result, Button, Icon } from 'antd'

const PermissionDenied = (props) => {
  return (
    <Result
      title="403"
      icon={<Icon type="frown" />}
      subTitle="You do not have permission to access this page."
      extra={
        <Link to={props.to}>
          <Button type="primary">Go Back</Button>
        </Link>
      }
    />
  );
}

PermissionDenied.defaultProps = {
  to: "/"
}

export default PermissionDenied
