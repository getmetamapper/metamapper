import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter, Link } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { Table } from "antd"
import { map, debounce } from "lodash"
import { components } from "app/Common/EditableCell"
import UpdateTableMetadata from "graphql/mutations/UpdateTableMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreAssetsTable extends Component {
  constructor(props) {
    super(props)

    const {
      dataSource,
      datastore,
      currentWorkspace: { slug },
    } = props

    this.columns = [
      {
        title: "Schema Name",
        render: ({ schema }) => <span title={schema.name}>{schema.name}</span>,
      },
      {
        title: "Asset Name",
        render: ({ schema, name: tablename }) => (
          <Link
            to={`/${slug}/datastores/${datastore.slug}/definition/${schema.name}/${tablename}/overview`}
            title={tablename}
          >
            {tablename}
          </Link>
        ),
      },
      {
        title: "Asset Type",
        dataIndex: "kind",
        key: "kind",
      },
      {
        title: "Description",
        dataIndex: "shortDesc",
        key: "shortDesc",
        editable: true,
      },
    ]

    window.onscroll = debounce(() => {
      // Bails early if:
      // * it's already loading
      // * there's nothing left to load
      if (this.state.loading || !this.props.hasNextPage) return;

      // Checks that the page has scrolled to the bottom
      if (
        document.documentElement.scrollTop + document.documentElement.offsetHeight
        >= (document.documentElement.scrollHeight * 0.985)
      ) {
        console.log('hit next page!')
        this.fetchNextPage()
      }
    }, 100);


    this.state = {
      dataSource,
      loading: false,
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    return nextState.dataSource.length !== this.state.dataSource.length || nextState.loading !== this.state.loading || nextState.nonce !== this.state.nonce
  }

  fetchNextPage = () => {
    this.setState({ loading: true })

    this.props.fetchNextPage().then(({ data }) => {
      const { datastoreAssets: { edges } } = data

      this.setState({
        loading: false,
        dataSource: [
          ...this.state.dataSource,
          ...map(edges, ({ node }) => node),
        ]
      })
    })
  }

  handleSave = (row) => {
    const payload = {
      variables: {
        id: row.id,
        shortDesc: row.shortDesc,
      },
      successMessage: "Description was saved.",
    }

    this.props.handleMutation(payload)
    this.updateRow(row)
  }

  updateRow = (row) => {
    const newData = [...this.state.dataSource]
    const index = newData.findIndex((item) => row.id === item.id)
    const item = newData[index]
    newData.splice(index, 1, {
      ...item,
      ...row,
    })
    this.setState({ dataSource: newData, nonce: Math.random() })
  }

  render() {
    const { hasPermission } = this.props
    const { dataSource, loading } = this.state
    const columns = this.columns.map((col) => {
      if (!hasPermission || !col.editable) {
        return col
      }
      return {
        ...col,
        onCell: (record) => ({
          record,
          editable: col.editable,
          dataIndex: col.dataIndex,
          title: col.title,
          handleSave: this.handleSave,
        }),
      }
    })
    return (
      <div data-test="DatastoreAssetsTable">
        <Table
          rowKey="id"
          rowClassName={() => "editable-row"}
          className="datastore-assets"
          dataSource={dataSource}
          components={components}
          columns={columns}
          pagination={false}
          loading={loading}
        />
      </div>
    )
  }
}

DatastoreAssetsTable.defaultProps = {
  datastore: {},
  dataSource: [],
}

const enhance = compose(
  withUserContext,
  withRouter,
  withWriteAccess,
  graphql(UpdateTableMetadata),
  withGraphQLMutation,
)

export default enhance(DatastoreAssetsTable)
