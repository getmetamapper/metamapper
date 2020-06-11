import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { withUserContext } from "context/UserContext"
import { withRouter, Link } from "react-router-dom"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { Table } from "antd"

import { map, uniqBy, flatten } from "lodash"
import { components } from "app/Common/EditableCell"
import UpdateTableMetadata from "graphql/mutations/UpdateTableMetadata"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class DatastoreAssetsTable extends Component {
  constructor(props) {
    super(props)

    const {
      datastore,
      schemas,
      currentWorkspace: { slug },
    } = props

    const dataSource = this.flattenDataSource(schemas)

    this.columns = [
      {
        title: "Schema Name",
        dataIndex: "schema",
        key: "schema",
        filters: map(uniqBy(dataSource, "schema"), ({ schema }) => ({
          text: schema,
          value: schema,
        })),
        onFilter: (value, record) => record.schema.indexOf(value) === 0,
      },
      {
        title: "Asset Name",
        render: ({ schema, tablename }) => (
          <Link
            to={`/${slug}/datastores/${datastore.slug}/definition/${schema}/${tablename}/overview`}
          >
            {tablename}
          </Link>
        ),
      },
      {
        title: "Asset Type",
        dataIndex: "kind",
        key: "kind",
        filters: map(uniqBy(dataSource, "kind"), ({ kind }) => ({
          text: kind,
          value: kind,
        })),
        onFilter: (value, record) => record.kind.indexOf(value) === 0,
      },
      {
        title: "Description",
        dataIndex: "shortDesc",
        key: "shortDesc",
        editable: true,
      },
    ]

    this.state = {
      dataSource,
    }
  }

  flattenDataSource = (dataSource) => {
    return flatten(
      map(dataSource, ({ name: schema, tables }) => {
        return map(tables, ({ id, name: tablename, kind, shortDesc }) => ({
          id,
          schema,
          tablename,
          kind,
          shortDesc,
        }))
      })
    )
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
    this.setState({ dataSource: newData })
  }

  render() {
    const { hasPermission } = this.props
    const { dataSource } = this.state

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
      <span data-test="DatastoreAssetsTable">
        <Table
          rowKey="id"
          rowClassName={() => "editable-row"}
          className="datastore-tables"
          dataSource={dataSource}
          components={components}
          columns={columns}
          pagination={false}
        />
      </span>
    )
  }
}

DatastoreAssetsTable.defaultProps = {
  datastore: {},
  schemas: [],
}

const enhance = compose(
  withUserContext,
  withRouter,
  withWriteAccess,
  graphql(UpdateTableMetadata),
  withGraphQLMutation
)

export default enhance(DatastoreAssetsTable)
