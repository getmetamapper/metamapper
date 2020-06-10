import React, { Component } from "react"
import { Drawer, Menu } from "antd"
import Profile from "app/UserSettings/Profile"
import Security from "app/UserSettings/Security"

const defaultDrawerProps = {
  className: "user-settings",
  placement: "right",
  title: "User Settings",
  width: 800,
}

class UserSettings extends Component {
  state = { current: "profile" }

  handleClick = ({ key }) => {
    this.setState({ current: key })
  }

  render() {
    const { current } = this.state
    const { currentUser, onClose, visible } = this.props
    return (
      <Drawer visible={visible} onClose={onClose} {...defaultDrawerProps}>
        <Menu
          onClick={this.handleClick}
          selectedKeys={[current]}
          mode="horizontal"
        >
          <Menu.Item key="profile">Profile</Menu.Item>
          <Menu.Item key="security">Security</Menu.Item>
        </Menu>
        {visible && current === "profile" && (
          <Profile currentUser={currentUser} />
        )}
        {visible && current === "security" && (
          <Security currentUser={currentUser} />
        )}
      </Drawer>
    )
  }
}

export default UserSettings
