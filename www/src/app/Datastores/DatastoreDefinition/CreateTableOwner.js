import React from "react"
import { compose, graphql } from "react-apollo"
import { Button, Icon, Select } from "antd"
import { filter } from "lodash"
import CreateAssetOwnerMutation from "graphql/mutations/CreateAssetOwner"
import withGetWorkspaceGroups from "graphql/withGetWorkspaceGroups"
import withGetWorkspaceUsers from "graphql/withGetWorkspaceUsers"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withLoader from "hoc/withLoader"
import { coalesce } from "lib/utilities"
import { withUserContext } from "context/UserContext"

class CreateTableOwner extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      classification: 'BUSINESS',
      workspaceUsers: [],
      workspaceGroups: [],
    }

    this.handleClearOnClose = this.handleClearOnClose.bind(this)
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.open === false) {
      this.handleClearOnClose()
    }
  }

  handleSearch = value => {
    const { workspaceGroups, workspaceUsers } = this.props

    this.setState({
      workspaceGroups: this.handleFilter(workspaceGroups, value),
      workspaceUsers: this.handleFilter(workspaceUsers, value),
    })
  };

  handleFilter = (collection, value) => {
    const { ownerIds } = this.props
    return filter(collection, (record) => {
      return record.name.toLowerCase().indexOf(value.toLowerCase()) >= 0 && ownerIds.indexOf(coalesce(record.userId, record.id)) < 0
    })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    const { value: { key: ownerId }, classification } = this.state
    const { objectId } = this.props

    const payload = {
      successMessage: "Owner has been added.",
      variables: {
        ownerId,
        objectId,
        classification,
      },
      refetchQueries: ["GetTableDefinitionWithOwners"],
    }

    this.props.handleMutation(payload, this.handleSubmitSuccess)
  }

  handleSubmitSuccess = ({ data }) => {
    const { errors } = data.createAssetOwner

    if (!errors || errors.length === 0) {
      this.props.onClose()
      this.handleClearOnClose()
    }
  }

  handleClearOnClose = () => {
    this.setState({ typedValue: undefined })
  }

  handleChange = (value) => {
    let typedValue
    if (value) {
      typedValue = value
    }
    this.setState({
      value,
      typedValue,
    })
  }

  render() {
    const { typedValue } = this.state
    const { submitting } = this.props
    const dataSource = [
      {
        title: 'Groups',
        children: this.state.workspaceGroups,
      },
      {
        title: 'Users',
        children: this.state.workspaceUsers,
      },
    ];
    return (
      <div className="table-owner-search-wrapper">
        <Select
          allowClear
          className="table-owner-search"
          data-test="CreateAssetOwner.Input"
          dropdownClassName="table-owner-search-dropdown"
          filterOption={false}
          labelInValue
          notFoundContent={null}
          onChange={this.handleChange}
          onInputKeyDown={() => this.handleChange(null)}
          onSearch={this.handleSearch}
          placeholder="Enter a user or group..."
          showArrow={false}
          showSearch
          value={typedValue}
          size="large"
          style={{ width: 300 - 42 }}
        >
          {dataSource
            .map(group => (
              <Select.OptGroup key={group.title} label={group.title}>
                {group.children.map(opt => (
                  <Select.Option key={opt.pk} value={coalesce(opt.userId, opt.id)}>
                    {opt.name}
                  </Select.Option>
                ))}
              </Select.OptGroup>
            ))
          }
        </Select>
        <div>
          <Select value={this.state.classification} onChange={(classification) => this.setState({ classification })}>
            <Select.Option value="TECHNICAL">Technical</Select.Option>
            <Select.Option value="BUSINESS">Business</Select.Option>
          </Select>
        </div>
        <div>
          <Button
            block
            type="primary"
            size="small"
            onClick={this.handleSubmit}
            disabled={submitting}
            data-test="CreateAssetOwner.Submit"
          >
            <Icon type={submitting ? 'loading' : 'check'} />
          </Button>
        </div>
      </div>
    )
  }
}

const withPopoverLoader = withLoader({
  size: "small",
  wrapperstyles: {
    textAlign: "center",
    margin: "10px 40px"
  },
})

export default compose(
  withUserContext,
  withGetWorkspaceUsers,
  withGetWorkspaceGroups,
  withPopoverLoader,
  graphql(CreateAssetOwnerMutation),
  withGraphQLMutation,
)(CreateTableOwner)
