import React from "react"

const InfoItem = ({ label, value }) => (
  <div className="info-item">
    <label className="info-item-label">
      {label}
    </label>
    <span className="info-item-value">
      {value}
    </span>
  </div>
)

export default InfoItem
