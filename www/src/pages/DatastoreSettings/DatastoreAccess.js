import React, { Component } from "react"
import { compose } from "react-apollo"
import { withRouter } from "react-router-dom"
import { Card, Col, Divider, Form, Row, Alert, Icon, Spin } from "antd"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { withLargeLoader } from "hoc/withLoader"
import ToggleDatastoreObjectPermissions from "app/Datastores/DatastoreAccess/ToggleDatastoreObjectPermissions"
import DatastoreAccessContainer from "app/Datastores/DatastoreAccess/DatastoreAccessContainer"
import DatastoreLayout from "app/Datastores/DatastoreLayout"
import withGetDatastoreSettings from "graphql/withGetDatastoreSettings"
import withNotFoundHandler from "hoc/withNotFoundHandler"


class DatastoreAccess extends Component {
  constructor(props) {
    super(props)

    const {
      datastore: { objectPermissionsEnabled }
    } = props

    this.state = {
      isEnabled: objectPermissionsEnabled,
      isToggling: false,
    }

    this.breadcrumbs = this.breadcrumbs.bind(this)
    this.handleToggleStarted = this.handleToggleStarted.bind(this)
    this.handleToggleFinished = this.handleToggleFinished.bind(this)
  }

  breadcrumbs(datastore) {
    const {
      currentWorkspace: { slug },
      match: {
        params: { datastoreSlug },
      },
    } = this.props

    return [
      {
        label: "Datastores",
        to: `/${slug}/datastores`,
      },
      {
        label: datastoreSlug,
        to: `/${slug}/datastores/${datastoreSlug}`,
      },
      {
        label: "Access",
      },
    ]
  }

  handleToggleStarted = () => {
    this.setState({ isToggling: true })
  }

  handleToggleFinished = (isEnabled) => {
    this.setState({ isEnabled, isToggling: false })
  }

  render() {
    const {
      currentWorkspace,
      datastore,
      hasPermission,
      loading,
    } = this.props
    const {
      isEnabled,
      isToggling,
    } = this.state
    return (
      <DatastoreLayout
        breadcrumbs={this.breadcrumbs}
        datastore={datastore}
        loading={loading}
        title={`Access - ${datastore.slug} - Metamapper`}
      >
        <Row>
          <Col span={16} offset={4}>
            <Card className="datastore-access">
              <div className="datastore-access-header">
                <h3>Datastore Access Settings</h3>
                <Divider />
                <Row style={{ marginBottom: 24 }}>
                  <Col>
                    <Alert message={
                      <span>
                        This section allows you to configure Metamapper-specific permissions
                        for the <b>{datastore.name}</b> datastore. Changing the settings will never
                        affect the permission grants of your connected database.
                      </span>
                    }/>
                  </Col>
                </Row>
                <ToggleDatastoreObjectPermissions
                  datastore={datastore}
                  hasPermission={hasPermission}
                  isEnabled={isEnabled}
                  onStartChange={this.handleToggleStarted}
                  onFinishChange={this.handleToggleFinished}
                />
                <Divider />
                {isToggling && (
                  <div className="toggling">
                    <Spin size="large" indicator={<Icon type="loading" />} />
                  </div>
                )}
                {isEnabled && !isToggling && (
                  <DatastoreAccessContainer
                    datastore={datastore}
                    currentWorkspace={currentWorkspace}
                    hasPermission={hasPermission}
                  />
                )}
              </div>
            </Card>
         </Col>
        </Row>
      </DatastoreLayout>
    )
  }
}

const withForm = Form.create()

const withNotFound = withNotFoundHandler(({ datastore }) => {
  return !datastore || !datastore.hasOwnProperty("id")
})

const enhance = compose(
  withForm,
  withRouter,
  withWriteAccess,
  withGetDatastoreSettings,
  withLargeLoader,
  withNotFound,
)

export default enhance(DatastoreAccess)
