import React, { Component, Fragment } from "react"
import { Button, Icon, Input, Table } from "antd"
import { coalesce } from "lib/utilities"
import DisplayUsername from "app/WorkspaceSettings/Users/DisplayUsername"
import withGetWorkspaceGroupUsers from "graphql/withGetWorkspaceGroupUsers"
import { withLargeLoader } from "hoc/withLoader"

class ManageGroupUsersTable extends Component {
  constructor(props) {
    super(props)

    this.state = {
      searchText: '',
      searchedColumn: '',
    }
  }

  getColumnSearchProps = dataIndex => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }}>
        <Input
          ref={node => {
            this.searchInput = node;
          }}
          placeholder={`Search ${dataIndex}`}
          data-test="GroupUsersTable.SearchInput"
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => this.handleSearch(selectedKeys, confirm, dataIndex)}
          style={{ width: 188, marginBottom: 8, display: 'block' }}
        />
        <Button
          type="primary"
          onClick={() => this.handleSearch(selectedKeys, confirm, dataIndex)}
          icon="search"
          size="small"
          style={{ width: 90, marginRight: 8 }}
          data-test="GroupUsersTable.SearchSubmit"
        >
          Search
        </Button>
        <Button onClick={() => this.handleReset(clearFilters)} size="small" style={{ width: 90 }}>
          Reset
        </Button>
      </div>
    ),
    filterIcon: filtered => (
      <Icon
        type="search"
        style={{ color: filtered ? '#1890ff' : undefined }}
        data-test="GroupUsersTable.SearchIcon"
      />
    ),
    onFilter: (value, record) => {
      return record[dataIndex]
        .toString()
        .toLowerCase()
        .includes(value.toLowerCase())
    },
    onFilterDropdownVisibleChange: visible => {
      if (visible) {
        setTimeout(() => this.searchInput.select());
      }
    },
  });


  handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    this.setState({
      searchText: selectedKeys[0],
      searchedColumn: dataIndex,
    });
  };

  handleReset = clearFilters => {
    clearFilters();
    this.setState({ searchText: '' });
  };

  render() {
    const { hasPermission, workspaceGroupUsers } = this.props

    const columns = [
      {
        title: "User",
        dataIndex: "name",
        colSpan: 2,
        sorter: (a, b) => coalesce(b.name, b.email).charCodeAt(0),
        render: (text, record) => <DisplayUsername {...record} />,
        ...this.getColumnSearchProps('name'),
      },
    ]

    if (hasPermission) {
      columns.push({
        align: "right",
        colSpan: 0,
        render: (record) => (
          <Fragment>
            {/* eslint-disable-next-line*/}
            <a
              role="button"
              onClick={() => this.props.onRemove(record)}
              className="mr-10"
            >
              Remove
            </a>
          </Fragment>
        ),
      })
    }
    return (
      <span className="groups-table" data-test="GroupUsersTable">
        <Table
          rowKey="id"
          dataSource={workspaceGroupUsers}
          columns={columns}
          pagination={{ pageSize: 5 }}
        />
      </span>
    )
  }
}

export default withGetWorkspaceGroupUsers(withLargeLoader(ManageGroupUsersTable))
