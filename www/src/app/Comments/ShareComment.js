import React, { Component } from "react"
import { Popover } from "antd"
import CopyInput from "app/Common/CopyInput"

class ShareComment extends Component {
  state = {
    visible: false,
  }

  hide = () => {
    this.setState({
      visible: false,
    })
  }

  handleVisibleChange = (visible) => {
    this.setState({ visible })
  }

  render() {
    return (
      <Popover
        content={<CopyInput value="test" disabled />}
        title={null}
        trigger="click"
        visible={this.state.visible}
        onVisibleChange={this.handleVisibleChange}
      >
        <span key="comment-share">share</span>
      </Popover>
    )
  }
}

export default ShareComment
