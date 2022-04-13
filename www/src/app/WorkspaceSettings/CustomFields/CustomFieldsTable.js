import React, { Component, Fragment } from "react"
import { Table, Tag } from "antd"
import { fieldToNameMapping } from "./CustomFieldFieldset"
import withGetCustomFields from "graphql/withGetCustomFields"

class CustomFieldsTable extends Component {
  constructor(props) {
    super(props)

    this.columns = [
      {
        title: "Field Name",
        dataIndex: "fieldName",
        key: "fieldName",
      },
      {
        title: "Type",
        dataIndex: "fieldType",
        key: "fieldType",
        render: (fieldType) => <Tag>{fieldToNameMapping[fieldType]}</Tag>,
      },
      {
        title: "Description",
        dataIndex: "shortDesc",
        key: "shortDesc",
      },
    ]

    if (props.hasPermission) {
      this.columns.push({
        align: "right",
        render: (record) => (
          <Fragment>
            {/* eslint-disable-next-line*/}
            <a
              role="button"
              onClick={() => props.onUpdate(record)}
              className="mr-10"
            >
              Edit
            </a>
            {/* eslint-disable-next-line*/}
            <a role="button" onClick={() => props.onDelete(record)}>
              Delete
            </a>
          </Fragment>
        ),
      })
    }
  }

  render() {
    const { customFields } = this.props
    return (
      <span className="custom-fields-table" data-test="CustomFieldsTable">
        <Table
          rowKey="pk"
          dataSource={customFields}
          columns={this.columns}
          pagination={false}
        />
      </span>
    )
  }
}

export default withGetCustomFields(CustomFieldsTable)
