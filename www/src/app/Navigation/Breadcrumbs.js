import React from "react"
import { Breadcrumb } from "antd"
import { Link } from "react-router-dom"
import { map } from "lodash"

const Breadcrumbs = ({ breadcrumbs }) => (
  <div className="breadcrumbs">
    <Breadcrumb>
      {map(breadcrumbs, (breadcrumb, idx) => (
        <Breadcrumb.Item key={idx}>
          {breadcrumb && breadcrumb.hasOwnProperty("to") ? (
            <Link to={breadcrumb.to}>{breadcrumb.label}</Link>
          ) : (
            <span>{breadcrumb.label}</span>
          )}
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  </div>
)

Breadcrumbs.defaultProps = {
  breadcrumbs: [],
}

export default Breadcrumbs
