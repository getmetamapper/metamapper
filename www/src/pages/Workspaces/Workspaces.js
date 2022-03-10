import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { compose } from "react-apollo"
import { Button, Col, Row, message } from "antd"
import { withLargeLoader } from "hoc/withLoader"
import { withRouter } from "react-router-dom"
import WorkspaceList from "app/Workspaces/WorkspaceList"
import WorkspaceSetup from "app/Workspaces/WorkspaceSetup"
import qs from "query-string"

class Workspaces extends Component {
  static defaultProps = {
    loading: true,
  }

  constructor(props) {
    super(props);

    const {
      deleted
    } = qs.parse(props.location.search)

    if (deleted) {
      message.success("Workspace has been deleted.")
    }

    this.state = {
      setupVisible: false
    }
  }

  onOpenSetupForm = () => {
    this.setState({ setupVisible: true })
  }

  onCloseSetupForm = () => {
    this.setState({ setupVisible: false })
  }

  selectWorkspace = (workspace) => {
    this.props.config.setCurrentWorkspace(workspace)
    this.props.refreshUser()

    window.location.href = `/${workspace.slug}`
  }

  render() {
    const { loading, myWorkspaces } = this.props
    const { setupVisible } = this.state
    return (
      <Row>
        <Helmet>
          <title>Workspaces - Metamapper</title>
        </Helmet>
        <Col span={8} offset={8}>
          <div className="create-workspace-btn">
            <Button block type="primary" onClick={this.onOpenSetupForm}>
              Create New Workspace
            </Button>
          </div>
          <WorkspaceList
            workspaces={myWorkspaces}
            loading={loading}
            onClick={this.selectWorkspace}
          />
        </Col>
        <>
          <WorkspaceSetup
            visible={setupVisible}
            onCancel={this.onCloseSetupForm}
          />
        </>
      </Row>
    )
  }
}


export default compose(
  withRouter,
  withLargeLoader,
)(Workspaces)
