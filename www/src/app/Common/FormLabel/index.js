import React from "react"
import PropTypes from "prop-types"
import { Icon, Popover } from "antd"

import "./index.css"

const FormLabel = ({ label, required, helpText, helpPlacement }) => {
  let helpTextComponent = ""

  if (helpText !== "") {
    helpTextComponent = (
      <span className="popover">
        <Popover content={helpText} placement={helpPlacement}>
          <Icon type="question-circle" theme="filled" />
        </Popover>
      </span>
    )
  }

  return (
    <div className="form-label">
      <label
        className={required ? "ant-form-item-required" : "ant-form-item"}
        title={label}
      >
        {label}
      </label>
      {helpTextComponent}
    </div>
  )
}

FormLabel.propTypes = {
  label: PropTypes.string.isRequired,
  required: PropTypes.bool,
  helpText: PropTypes.string,
}

FormLabel.defaultProps = {
  required: false,
  helpText: "",
  helpPlacement: "top"
}

export default FormLabel
