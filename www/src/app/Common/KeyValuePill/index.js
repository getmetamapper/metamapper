import React from "react"
import PropTypes from "prop-types"

const KeyValuePill = ({ keyname, value }) => (
  <div className="pill-group">
    <span className="pill keyname">{keyname}</span>
    <span className="pill value">{value}</span>
  </div>
)

KeyValuePill.propTypes = {
  keyname: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
}

export default KeyValuePill
