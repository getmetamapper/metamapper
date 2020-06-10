import React, { Component } from "react"
import { Select } from "antd"
import { concat, map, pull, indexOf } from "lodash"

class TagsInput extends Component {
  constructor(props) {
    super(props)

    this.state = {
      tags: props.value || [],
    }
  }

  handleSelect = (tag) => {
    const { tags } = this.state

    if (indexOf(tags, tag) < 0) {
      this.setState({
        tags: concat(tags, tag),
      })
    }
  }

  handleDeselect = (tag) => {
    const { tags } = this.state

    this.setState({
      tags: pull(tags, tag),
    })
  }

  handleChange = (tags) => {
    if (this.props.onChange) {
      this.props.onChange(tags)
    }
  }

  render() {
    const { tags } = this.state
    const { className, placeholder, disabled, ...restProps } = this.props
    return (
      <Select
        mode="tags"
        className={`tags-input ${className}`}
        defaultValue={tags}
        disabled={disabled}
        placeholder={placeholder}
        onChange={this.handleChange}
        onSelect={this.handleSelect}
        onDeselect={this.handleDeselect}
        {...restProps}
      >
        {map(tags, (tag) => (
          <Select.Option key={tag} value={tag}>
            {tag}
          </Select.Option>
        ))}
      </Select>
    )
  }
}

TagsInput.defaultProps = {
  className: "tags-input",
  placeholder: "",
}

export default TagsInput
