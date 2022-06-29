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
import TableSchemaSelector from "app/Datastores/DatastoreDefinition/TableSchemaSelector"

const InnerDatastoreLayout = withLargeLoader(({ children, datastore, loading, hideSchemaSelector }) => (
  <Row>
    <Col span={hideSchemaSelector ? 24 : 20}>
      <div className="inner-datastore-layout">{children}</div>
    </Col>
    {!hideSchemaSelector && (
      <Col span={4} className="table-schema-selector-wrapper">
        <TableSchemaSelector
          currentTable={{ name: null }}
          datastore={datastore}
          loading={loading}
        />
      </Col>
    )}
  </Row>
))

class DatastoreLayout extends Component {
  constructor(props) {
    super(props)

    const {
      config,
      match: {
        params: { datastoreSlug },
      },
    } = props

    config.setDatastoreSlug(datastoreSlug)
  }

  getBaseUri() {
    const {
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    return `/${slug}/datastores/${datastoreSlug}`
  }

  getLinks() {
    const baseUri = this.getBaseUri()
    const { datastore } = this.props
    const links = [
      {
        icon: "dashboard",
        label: "Overview",
        to: baseUri,
        visible: true,
      },
      {
        icon: "read",
        label: "Assets",
        to: `${baseUri}/assets`,
        visible: true,
      },
      {
        icon: "check-circle",
        label: "Checks",
        to: `${baseUri}/checks`,
        visible: datastore.supportedFeatures.checks,
      },
      {
        icon: "sync",
        label: "Run History",
        to: `${baseUri}/runs`,
        visible: true,
      },
      {
        icon: "database",
        label: "Connection",
        to: `${baseUri}/connection`,
        visible: true,
      },
      {
        icon: "user",
        label: "Access",
        to: `${baseUri}/access`,
        visible: true,
      },
      {
        icon: "setting",
        label: "Settings",
        to: `${baseUri}/settings`,
        visible: true,
      },
    ]

    return links.filter((l) => l.visible)
  }

  render() {
    const {
      breadcrumbs,
      className,
      children,
      datastore,
      loading,
      title,
      hideSchemaSelector,
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
              <Col span={1} className="fixed">
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
                    <Link to={this.getBaseUri()}>
                      <DatastoreEngineIcon datastore={datastore} noTooltip />
                    </Link>
                  )}
                </div>
                <Menu
                  className="datastores-menu"
                  mode="inline"
                  selectedKeys={[pathname]}
                >
                  {map(this.getLinks(), (link) => (
                    <Menu.Item key={link.to}>
                      <Tooltip title={link.label} placement="right">
                        <Link to={link.to}>
                          <Icon type={link.icon} />
                        </Link>
                      </Tooltip>
                    </Menu.Item>
                  ))}
                </Menu>
              </Col>
              <Col span={23} className="pull-right">
                <div className="breadcrumbs-wrapper fixed" data-test="DatastoreLayout.Breadcrumbs">
                  <Breadcrumbs breadcrumbs={breadcrumbs(datastore)} />
                </div>
                <Layout.Content className={className}>
                  <InnerDatastoreLayout
                    children={children}
                    datastore={datastore}
                    loading={loading}
                    hideSchemaSelector={hideSchemaSelector}
                  />
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
  hideSchemaSelector: false,
}

export default compose(withRouter, withUserContext)(DatastoreLayout)
