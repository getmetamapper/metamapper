import React, { PureComponent } from "react"
import { Input } from "antd"

import "./index.css"

class PasswordInput extends PureComponent {
  state = {
    value: this.props.value || "",
    strength: -1,
  }

  componentWillReceiveProps(nextProps) {
    if ("value" in nextProps) {
      this.setState({ value: nextProps.value })
    }
  }

  handleChange = (e) => {
    if (!("value" in this.props)) {
      const { value } = e.target

      this.setState({ value })
    }

    if (this.props.onChange) {
      this.props.onChange(e)
    }

    let strength = -1

    if (this.state.value && this.props.strengthMeter && window.zxcvbn) {
      strength = window.zxcvbn(this.state.value).score
    }

    this.setState({ strength })
  }

  render() {
    const { tooltip, strengthMeter, ...otherProps } = this.props
    const { value, strength } = this.state

    const strengthClass = [
      "strength-meter",
      value && value.length > 0 ? "visible" : "invisible",
    ]
      .join(" ")
      .trim()

    return (
      <div className="input-password">
        <Input.Password
          {...otherProps}
          value={this.state.value}
          onChange={this.handleChange}
        />
        {strengthMeter && (
          <div className={strengthClass}>
            <div className="strength-meter-fill" data-strength={strength} />
          </div>
        )}
      </div>
    )
  }
}

export default PasswordInput
