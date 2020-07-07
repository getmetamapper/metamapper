import React, { Component } from "react"
import { compose } from "react-apollo"
import { Col, Row, Input, Icon, Button } from "antd"
import { filter } from "lodash"
import { withLargeLoader } from "hoc/withLoader"
import DatastoreAccessPrivilegesTable from "./DatastoreAccessPrivilegesTable"
import GrantDatastoreUserAccess from "./GrantDatastoreUserAccess"
import GrantDatastoreGroupAccess from "./GrantDatastoreGroupAccess"
import withGetDatastoreAccessPrivileges from "graphql/withGetDatastoreAccessPrivileges"


const DatastoreAccessContainer = ({ datastoreGroups, datastoreUsers, ...restProps }) => (
  <InnerDatastoreAccessContainer
    datastoreUsers={datastoreUsers}
    datastoreGroups={datastoreGroups}
    {...restProps}
  />
)

class InnerDatastoreAccessContainer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      // Current state of the table data.
      accessGroups: props.datastoreGroups,
      accessTeamMembers: props.datastoreUsers,

      // We cache the existing users so we can filter back to zero.
      accessGroupsCache: props.datastoreGroups,
      accessTeamMembersCache: props.datastoreUsers,

      // For controlling the pop-up dialogs.
      groupVisible: false,
      userVisible: false,

      // Random number so we can reset state when queries come through, if needed.
      nonce: props.nonce,

      // We cache the search query for componentWillReceiveProps
      searchQuery: '',
    }
  }

  componentWillReceiveProps(nextProps) {
    const { datastoreGroups, datastoreUsers } = nextProps
    const { searchQuery } = this.state

    const newState = {
      nonce: nextProps.nonce,
    }

    if (newState.nonce !== this.state.nonce) {
      // Reload the groups associated with the datatore.
      newState["accessGroupsCache"] = datastoreGroups
      newState["accessGroups"] = this.searchCollection(datastoreGroups, searchQuery)

      // Reload the users associated with the datastore.
      newState["accessTeamMembersCache"] = datastoreUsers
      newState["accessTeamMembers"] = this.searchCollection(datastoreUsers, searchQuery)
    }

    if (Object.keys(newState).length > 0) {
      this.setState(newState)
    }
  }

  searchCollection = (collection, query) => {
    return filter(collection, ({ name }) => name.toLowerCase().indexOf(query) > -1)
  }

  handleSearch = (e) => {
    const {
      accessGroupsCache,
      accessTeamMembersCache,
    } = this.state

    const searchQuery = e.target.value.toLowerCase()

    const accessGroups = this.searchCollection(
      accessGroupsCache,
      searchQuery,
    )

    const accessTeamMembers = this.searchCollection(
      accessTeamMembersCache,
      searchQuery,
    )

    this.setState({
      accessGroups,
      accessTeamMembers,
      searchQuery,
    })
  }

  onOpenGrantUserForm = () => {
    this.setState({ userVisible: true })
  }

  onCloseGrantUserForm = () => {
    this.setState({ userVisible: false })
  }

  onOpenGrantGroupForm = () => {
    this.setState({ groupVisible: true })
  }

  onCloseGrantGroupForm = () => {
    this.setState({ groupVisible: false })
  }

  render() {
    const {
      datastore,
      hasPermission,
    } = this.props
    const {
      accessGroups,
      accessTeamMembers,
      groupVisible,
      userVisible,
    } = this.state
    return (
      <>
        <Row className="mb-20">
          <Col>
            <Input
              suffix={<Icon type="search" style={{ color: "rgba(0,0,0,.25)" }} />}
              type="text"
              placeholder="Search for user or group..."
              size="small"
              onChange={this.handleSearch}
            />
          </Col>
        </Row>
        <Row className="mb-20">
          <Col>
            <h3>Groups</h3>
            <p>
              These are the permissions currently assigned to groups for this datastore.
            </p>
            <Button type="primary" onClick={this.onOpenGrantGroupForm} data-test="GrantGroupAccessButton">
              Grant group access
            </Button>
            <DatastoreAccessPrivilegesTable
              contentType="GROUP"
              dataSource={accessGroups}
              datastore={datastore}
              dataTest="DatastoreAccessGroupPrivilegesTable"
              hasPermission={hasPermission}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <h3>Individual Users</h3>
            <p>
              These are the permissions currently assigned to individual users for this
              datastore. Users with the <b>Owner</b> role are not affected by this list.
            </p>
            <Button type="primary" onClick={this.onOpenGrantUserForm} data-test="GrantUserAccessButton">
              Grant user access
            </Button>
            <DatastoreAccessPrivilegesTable
              contentType="USER"
              dataSource={accessTeamMembers}
              datastore={datastore}
              dataTest="DatastoreAccessUserPrivilegesTable"
              hasPermission={hasPermission}
            />
          </Col>
        </Row>
        <>
          <GrantDatastoreUserAccess
            datastore={datastore}
            visible={userVisible}
            onCancel={this.onCloseGrantUserForm}
          />
          <GrantDatastoreGroupAccess
            datastore={datastore}
            visible={groupVisible}
            onCancel={this.onCloseGrantGroupForm}
          />
        </>
      </>
    )
  }
}

export default compose(
  withGetDatastoreAccessPrivileges,
  withLargeLoader,
)(DatastoreAccessContainer)
