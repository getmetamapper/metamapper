import React, { Component } from "react"
import { compose } from "react-apollo"
import { Icon, Table, Tag, Button, Input } from "antd"
import { renderRevisionText } from "app/Datastores/Revisions/RevisionText"
import { renderRevisionIcon } from "app/Datastores/Revisions/RevisionIcon"
import moment from "moment"
import withGetRunRevisions from "graphql/withGetRunRevisions"
import { withLargeLoader } from "hoc/withLoader"

class TableRevisionLog extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Action",
        dataIndex: "action",
        render: renderRevisionIcon,
        filters: [
          { text: "Created", value: "CREATED" },
          { text: "Modified", value: "MODIFIED" },
          { text: "Dropped", value: "DROPPED" },
        ],
        onFilter: (value, record) =>
          record.action.toUpperCase().indexOf(value) === 0,
      },
      {
        title: "Type",
        dataIndex: "relatedResource.type",
        render: (type) => <Tag>{type}</Tag>,
        filters: [
          { text: "Schema", value: "Schema" },
          { text: "Table", value: "Table" },
          { text: "Column", value: "Column" },
          { text: "Index", value: "Index" },
        ],
        onFilter: (value, { relatedResource }) =>
          relatedResource.type.indexOf(value) === 0,
      },
      {
        title: "Identifier",
        dataIndex: "relatedResource",
        render: ({ label }) => <Tag>{label}</Tag>,
        ...this.getColumnSearchProps("relatedResource", ({ label }) => label),
      },
      {
        title: "Applied On",
        key: "appliedOn",
        dataIndex: "appliedOn",
        render: (appliedOn) => (
          <Tag>{moment(appliedOn).format("YYYY-MM-DD")}</Tag>
        ),
      },
      {
        title: "Activity",
        render: renderRevisionText,
      },
    ]

    this.state = {
      searchText: "",
      searchedColumn: "",
    }
  }

  handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm()
    this.setState({
      searchText: selectedKeys[0],
      searchedColumn: dataIndex,
    })
  }

  handleReset = (clearFilters) => {
    clearFilters()
    this.setState({ searchText: "" })
  }

  getColumnSearchProps = (dataIndex, attributeCallback = (value) => value) => ({
    filterDropdown: ({
      setSelectedKeys,
      selectedKeys,
      confirm,
      clearFilters,
    }) => (
      <div style={{ padding: 8 }}>
        <Input
          ref={(node) => {
            this.searchInput = node
          }}
          placeholder="Type to search..."
          value={selectedKeys[0]}
          onChange={(e) =>
            setSelectedKeys(e.target.value ? [e.target.value] : [])
          }
          onPressEnter={() =>
            this.handleSearch(selectedKeys, confirm, dataIndex)
          }
          style={{ width: 188, marginBottom: 8, display: "block" }}
        />
        <Button
          type="primary"
          onClick={() => this.handleSearch(selectedKeys, confirm, dataIndex)}
          icon="search"
          size="small"
          style={{ width: 90, marginRight: 8 }}
        >
          Search
        </Button>
        <Button
          onClick={() => this.handleReset(clearFilters)}
          size="small"
          style={{ width: 90 }}
        >
          Reset
        </Button>
      </div>
    ),
    filterIcon: (filtered) => (
      <Icon type="search" style={{ color: filtered ? "#1890ff" : undefined }} />
    ),
    onFilter: (value, record) =>
      attributeCallback(record[dataIndex])
        .toString()
        .toLowerCase()
        .includes(value.toLowerCase()),
    onFilterDropdownVisibleChange: (visible) => {
      if (visible) {
        setTimeout(() => this.searchInput.select())
      }
    },
  })

  render() {
    const { runRevisions } = this.props
    return (
      <Table
        rowKey="id"
        dataSource={runRevisions}
        columns={this.columns}
        pagination={false}
      />
    )
  }
}

TableRevisionLog.defaultProps = {
  runRevisions: [],
}

export default compose(withGetRunRevisions, withLargeLoader)(TableRevisionLog)
