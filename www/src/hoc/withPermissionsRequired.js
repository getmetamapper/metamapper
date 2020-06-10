import React from "react"
import { Alert, Col, Row } from "antd"
import { withUserContext } from "context/UserContext"

const withPermissionsRequired = ({ roles, message = null }) => (
  ChildComponent
) => {
  const withPermissions = (props) => {
    let hasPermission = false

    if (props.currentUser) {
      const { currentMembership } = props.currentUser

      if (currentMembership) {
        hasPermission = roles.indexOf(currentMembership.permissions.toUpperCase()) > -1
      }
    }

    return (
      <>
        {!hasPermission && message && (
          <Row className="permission-denied">
            <Col span={16}>
              <Alert message={message} type="warning" showIcon />
            </Col>
          </Row>
        )}
        <ChildComponent hasPermission={hasPermission} {...props} />
      </>
    )
  }

  return withUserContext(withPermissions)
}

export const withOwnersOnly = withPermissionsRequired({
  roles: ["OWNER"],
  message:
    "These settings can only be edited by users with the administrator role.",
})

export const withWriteAccess = withPermissionsRequired({
  roles: ["OWNER", "MEMBER"],
})

export const withSuperUserAccess = withPermissionsRequired({
  roles: ["OWNER"],
})

export default withPermissionsRequired
