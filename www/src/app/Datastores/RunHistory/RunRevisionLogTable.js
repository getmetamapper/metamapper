import React, { Component } from "react"
import { map, filter } from "lodash"
import { Icon, Table, Tag, Button, Input, Divider, Checkbox } from "antd"
import { renderRevisionText } from "app/Datastores/Revisions/RevisionText"
import { renderRevisionIcon } from "app/Datastores/Revisions/RevisionIcon"

const actionTypeFilterOptions = [
  { text: "Created", value: 1 },
  { text: "Modified", value: 2 },
  { text: "Dropped", value: 3 },
];

const resourceTypeFilterOptions = [
  { text: "Schema", value: "schema" },
  { text: "Table", value: "table" },
  { text: "Column", value: "column" },
  { text: "Index", value: "index" },
];

class RunRevisionLogTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Action",
        dataIndex: "action",
        render: renderRevisionIcon,
        ...this.getSelectionSearchProps(actionTypeFilterOptions, "actions"),
      },
      {
        title: "Resource Type",
        dataIndex: "relatedResource.type",
        render: (type) => <Tag>{type}</Tag>,
        ...this.getSelectionSearchProps(resourceTypeFilterOptions, "types"),
      },
      {
        title: "Resource Name",
        dataIndex: "relatedResource",
        render: ({ name }) => <Tag>{name}</Tag>,
        ...this.getFreeTextSearchProps(),
      },
      {
        title: "Activity",
        render: renderRevisionText,
      },
    ]

    this.state = {
      dataSource: props.runRevisions,
      loading: false,
      actions: [],
      types: [],
      search: "",
    }
  }

  fetchNextPage = () => {
    this.setState({ loading: true })

    this.props.fetchNextPage().then(({ data }) => {
      const { runRevisions: { edges } } = data

      this.setState({
        loading: false,
        dataSource: [
          ...this.state.dataSource,
          ...map(edges, ({ node }) => node),
        ]
      })
    })
  }

  applyFilters = () => {
    this.props.onFilter({
      actions: this.state.actions,
      types: this.state.types,
      search: this.state.search,
    })
  }

  setStateKey = (stateKey, value, applyFilters) => {
    const state = {}
    state[stateKey] = value
    this.setState(state)
  }

  getSelectionSearchProps = (options, stateKey) => ({
    filterDropdown: ({
      setSelectedKeys,
      selectedKeys,
      confirm,
      clearFilters,
    }) => (
      <div className="select-filter-dropdown">
        <Checkbox.Group value={this.state[stateKey]} onChange={(values) => this.setStateKey(stateKey, values)}>
          {map(options, ({ text, value }) => (
            <Checkbox value={value}>{text}</Checkbox>
          ))}
        </Checkbox.Group>
        <Divider />
        <Button
          type="primary"
          onClick={this.applyFilters}
          size="small"
          style={{ width: 90, marginRight: 8 }}
        >
          Apply
        </Button>
        <Button
          onClick={() => this.setStateKey(stateKey, [])}
          size="small"
          style={{ width: 90 }}
        >
          Clear
        </Button>
      </div>
    ),
    filterIcon: (filtered) => (
      <Icon type="filter" style={{ color: this.state[stateKey].length > 0 ? "#1890ff" : undefined }} />
    )
  })

  getFreeTextSearchProps = () => ({
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
          value={this.state.search}
          onChange={(e) => this.setState({ search: e.target.value })}
          style={{ width: 188, marginBottom: 8, display: "block" }}
        />
        <Button
          type="primary"
          onClick={this.applyFilters}
          icon="search"
          size="small"
          style={{ width: 90, marginRight: 8 }}
        >
          Search
        </Button>
        <Button
          onClick={() => this.setStateKey('search', '')}
          size="small"
          style={{ width: 90 }}
        >
          Clear
        </Button>
      </div>
    ),
    filterIcon: (filtered) => (
      <Icon type="search" style={{ color: this.state.search.length > 0 ? "#1890ff" : undefined }} />
    )
  })

  render() {
    const { dataSource, loading } = this.props
    return (
      <div data-test="RunRevisionLogTable">
        <Table
          rowKey="id"
          dataSource={filter(dataSource, (r) => r.relatedResource !== null)}
          columns={this.columns}
          pagination={false}
          loading={loading}
        />
      </div>
    )
  }
}

export default RunRevisionLogTable
