import React, { Component } from "react"
import { compose } from "react-apollo"
import { Helmet } from "react-helmet"
import { Link, withRouter } from "react-router-dom"
import { map } from "lodash"
import { withUserContext } from "context/UserContext"
import { Avatar, Col, Row, Icon, Layout, Menu, Tooltip } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import Breadcrumbs from "app/Navigation/Breadcrumbs"
import DatastoreEngineIcon from "app/Datastores/DatastoreEngineIcon"

const InnerLayout = ({ children }) => <div>{children}</div>

const InnerDatastoreLayout = withLargeLoader(InnerLayout)

class DatastoreLayout extends Component {
  getLinks() {
    const {
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    const baseUri = `/${slug}/datastores/${datastoreSlug}`

    return [
      {
        icon: "dashboard",
        label: "Overview",
        to: baseUri,
      },
      {
        icon: "read",
        label: "Assets",
        to: `${baseUri}/assets`,
      },
      {
        icon: "sync",
        label: "Run History",
        to: `${baseUri}/runs`,
      },
      {
        icon: "database",
        label: "Connection",
        to: `${baseUri}/connection`,
      },
      {
        icon: "user",
        label: "Access",
        to: `${baseUri}/access`,
      },
      {
        icon: "setting",
        label: "Settings",
        to: `${baseUri}/settings`,
      },
    ]
  }

  render() {
    const {
      breadcrumbs,
      className,
      children,
      datastore,
      loading,
      title,
    } = this.props
    const {
      location: { pathname },
    } = this.props
    return (
      <Row className="datastores">
        <Helmet>
          <title>{title}</title>
        </Helmet>
        <Col span={24}>
          <div className="datastores-inner">
            <Row>
              <Col span={4} className="fixed">
                <div className="datastore-sidebar-header-wrapper">
                  {loading ? (
                    <>
                      <Avatar shape="square" />
                      <div className="datastore-header-name">
                        <div
                          style={{
                            borderTop: "10px solid #f2f2f2",
                            width: 150,
                            marginLeft: 10,
                            marginTop: 10,
                          }}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <DatastoreEngineIcon datastore={datastore} noTooltip />
                      <div className="datastore-sidebar-header-name">
                        <Tooltip title={datastore.name}>{datastore.name}</Tooltip>
                      </div>
                    </>
                  )}
                </div>
                <Menu
                  className="datastores-menu"
                  mode="inline"
                  selectedKeys={[pathname]}
                >
                  {map(this.getLinks(), (link) => (
                    <Menu.Item key={link.to}>
                      <Link to={link.to}>
                        <Icon type={link.icon} /> {link.label}
                      </Link>
                    </Menu.Item>
                  ))}
                </Menu>
              </Col>
              <Col span={20} className="pull-right">
                <div className="breadcrumbs-wrapper fixed">
                  <Breadcrumbs breadcrumbs={breadcrumbs(datastore)} />
                </div>
                <Layout.Content className={className}>
                  <InnerDatastoreLayout children={children} loading={loading} />
                </Layout.Content>
              </Col>
            </Row>
          </div>
        </Col>
      </Row>
    )
  }
}

DatastoreLayout.defaultProps = {
  className: "datastores-content",
}

const enhance = compose(withRouter, withUserContext)

export default enhance(DatastoreLayout)
