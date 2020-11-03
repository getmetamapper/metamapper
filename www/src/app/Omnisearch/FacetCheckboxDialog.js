import React, { Component } from "react"
import { Checkbox, Modal } from "antd"

class FacetCheckboxDialog extends Component {
  state = { selected: [] }

  handleChange = (selected) => {
    this.setState({ selected })
  }

  handleOk = () => {
    this.props.onChange(this.state.selected)
    this.props.onCancel()
  }

  render() {
    const { title, visible, onCancel, options } = this.props
    return (
      <Modal
        title={`Filter by: "${title}"`}
        visible={visible}
        onOk={this.handleOk}
        onCancel={onCancel}
      >
        <Checkbox.Group onChange={this.handleChange} options={options} />
      </Modal>
    )
  }
}

export default FacetCheckboxDialog
