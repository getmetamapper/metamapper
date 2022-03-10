import React, { Component } from "react"
import { compose } from "react-apollo"
import { Helmet } from "react-helmet"
import { Link, withRouter } from "react-router-dom"
import { withUserContext } from "context/UserContext"
import { Card, Col, Icon, Layout, Menu, Row } from "antd"
import { findIndex, map } from "lodash"
import Breadcrumbs from "app/Navigation/Breadcrumbs"

class WorkspaceLayout extends Component {
  constructor(props) {
    super(props)

    const {
      currentWorkspace: { slug },
    } = this.props

    this.links = [
      {
        icon: "setting",
        label: "General",
        to: `/${slug}/settings`,
      },
      {
        icon: "team",
        label: "Users",
        to: `/${slug}/settings/users`,
      },
      {
        icon: "safety",
        label: "Authentication",
        to: `/${slug}/settings/authentication`,
      },
      {
        icon: "block",
        label: "Groups",
        to: `/${slug}/settings/groups`,
      },
      {
        icon: "tool",
        label: "Properties",
        to: `/${slug}/settings/customproperties`,
      },
    ]
  }

  currentPageIndex = () => {
    const {
      match: { url },
    } = this.props
    return [findIndex(this.links, { to: url }).toString()]
  }

  render() {
    const { breadcrumbs, currentWorkspace, children, title } = this.props
    return (
      <Row>
        <Helmet>
          <title>{title}</title>
        </Helmet>
        <Col span={18} offset={4}>
          <div className="breadcrumbs-wrapper">
            <Breadcrumbs breadcrumbs={breadcrumbs(currentWorkspace)} />
          </div>
          <Card className="workspace-settings">
            <Row>
              <Col span={4}>
                <Menu
                  mode="inline"
                  defaultSelectedKeys={this.currentPageIndex()}
                >
                  <div className="dropdown-menu-header workspace-layout-header" title="Workspace Settings">
                    Workspace Settings
                  </div>
                  {map(this.links, ({ icon, label, to }, idx) => (
                    <Menu.Item key={idx}>
                      <Link to={to} title={label}>
                        <Icon type={icon} /> {label}
                      </Link>
                    </Menu.Item>
                  ))}
                </Menu>
              </Col>
              <Col span={20}>
                <Layout.Content className="workspace-settings-content">
                  {children}
                </Layout.Content>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    )
  }
}

export default compose(withRouter, withUserContext)(WorkspaceLayout)
