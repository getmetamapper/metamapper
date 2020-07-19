import React from "react"
import { Button, Tooltip } from "antd"

const RestrictedButton = ({
  isSubmitting,
  hasPermission,
  children,
  disabled,
  ...restProps
}) => (
  <Tooltip
    title={
      !hasPermission
        ? "You do not have permission to perform this action."
        : null
    }
  >
    <Button {...restProps} disabled={!hasPermission || isSubmitting || disabled}>
      {children}
    </Button>
  </Tooltip>
)

RestrictedButton.defaultProps = {
  isSubmitting: false,
}

export default RestrictedButton
