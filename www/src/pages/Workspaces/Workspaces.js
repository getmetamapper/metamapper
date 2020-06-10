import React, { Component } from "react"
import { Helmet } from "react-helmet"
import { Button, Col, Row } from "antd"
import WorkspaceList from "app/Workspaces/WorkspaceList"
import WorkspaceSetup from "app/Workspaces/WorkspaceSetup"

class Workspaces extends Component {
  state = { setupVisible: false }

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

export default Workspaces
