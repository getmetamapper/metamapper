import React, { useState } from "react"
import { compose } from "react-apollo"
import { withRouter, Link } from "react-router-dom"
import { Layout, Col, Row, Menu, Icon, Dropdown } from "antd"
import { withUserContext } from "context/UserContext"
import NavbarSearch from "app/Navigation/NavbarSearch"
import UserAvatar from "app/Common/UserAvatar"
import UserSettings from "app/UserSettings/UserSettings"

const Navbar = ({ config, currentUser }) => {
  const [settingsVisible, toggleSettings] = useState(false)
  const { email, fname, lname } = currentUser
  const currentWorkspace = config.getCurrentWorkspace()
  return (
    <Layout.Header className="top-navbar">
      <Row>
        <Col span={24}>
          <Link
            to={currentWorkspace ? `/${currentWorkspace.slug}` : "/"}
            className="logo"
          >
          <img src="/assets/static/img/brand/logo.png" alt="Metamapper" />
          </Link>
          <Menu
            mode="horizontal"
            theme="dark"
            style={{ float: "right", display: "inline-block" }}
          >
            <Menu.Item key="omnisearch" className="navbar-search">
              <NavbarSearch />
            </Menu.Item>
            {currentWorkspace && (
              <Menu.Item key="databases">
                <Link to={`/${currentWorkspace.slug}/datastores`}>
                  <Icon type="database" style={{ fontSize: "24px" }} />
                </Link>
              </Menu.Item>
            )}
            <Menu.Item key="dropdown" data-test="Navbar.Dropdown">
              <Dropdown
                className="navbar-dropdown"
                placement="bottomRight"
                trigger={["click"]}
                overlay={
                  <Menu>
                    <div className="top-navbar-dropdown">
                      <div className="avatar">
                        <UserAvatar noColor {...currentUser} />
                      </div>
                      <div className="user-details">
                        <div className="name">
                          {fname ? `${fname} ${lname}` : email}
                        </div>
                        <div className="email">{email}</div>
                      </div>
                    </div>
                    <Menu.Divider />
                    {currentWorkspace && (
                      <Menu.Item key="1">
                        <Link to={`/${currentWorkspace.slug}/settings`}>
                          Manage Workspace
                        </Link>
                      </Menu.Item>
                    )}
                    <Menu.Item key="2">
                      <Link to="https://github.com/metamapper-io/metamapper/">Help</Link>
                    </Menu.Item>
                    <Menu.Item key="3" onClick={() => toggleSettings(true)}>
                      User Settings
                    </Menu.Item>
                    <Menu.Divider />
                    <Menu.Item key="4">
                      <Link to="/workspaces" className="text-primary">
                        Change Workspace
                      </Link>
                    </Menu.Item>
                    <Menu.Item key="5">
                      <Link to="/logout">Sign Out</Link>
                    </Menu.Item>
                  </Menu>
                }
              >
                <span className="link ant-dropdown-link">
                  <UserAvatar noColor {...currentUser} />
                </span>
              </Dropdown>
            </Menu.Item>
          </Menu>
        </Col>
      </Row>
      {currentUser && (
        <UserSettings
          currentUser={currentUser}
          visible={settingsVisible}
          onClose={() => toggleSettings(false)}
        />
      )}
    </Layout.Header>
  )
}

export default compose(withRouter, withUserContext)(Navbar)
