import React from "react"
import BooleanIndicator from "app/Common/BooleanIndicator"

const BooleanStatus = ({ isEnabled }) => (
  <span className="boolean-status">
    <BooleanIndicator value={isEnabled} />
    <span className="text">
      {isEnabled ? 'Enabled' : 'Disabled'}
    </span>
  </span>
)

export default BooleanStatus
