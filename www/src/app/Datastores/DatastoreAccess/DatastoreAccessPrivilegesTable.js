import React, { Component, Fragment } from "react"
import { compose, graphql } from "react-apollo"
import { Table, Form, Button, Checkbox } from "antd"
import BooleanIndicator from "app/Common/BooleanIndicator"
import RevokeDatastoreAccess from "app/Datastores/DatastoreAccess/RevokeDatastoreAccess"
import UpdateDatastoreAccessPrivilegesMutation from "graphql/mutations/UpdateDatastoreAccessPrivileges"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import GetDatastoreAccessPrivileges from "graphql/queries/GetDatastoreAccessPrivileges"

const EditableCell = ({
  editing,
  dataIndex,
  title,
  form,
  record,
  name,
  index,
  children,
  ...restProps
}) => {
  return (
    <td {...restProps}>
      {editing ? (
        <Form.Item
          name={dataIndex}
          style={{
            margin: 0,
          }}
        >
          {form.getFieldDecorator(`privileges.${name}`, {
            initialValue: record.privileges.indexOf(name) > -1,
          })(
             <Checkbox defaultChecked={record.privileges.indexOf(name) > -1} />
          )}
        </Form.Item>
      ) : (
        children
      )}
    </td>
  );
};

class DatastoreAccessPrivilegesTable extends Component {
  state = { editingKey: '' }

  getColumns = () => {
    const { datastore } = this.props
    const columns = [
      {
        title: "Name",
        sorter: (a, b) => a.name.charCodeAt(0) - b.name.charCodeAt(0),
        render: (record) => <span>{record.name}</span>,
        visible: true,
      },
      {
        title: 'View',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'view_datastore',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('view_datastore') > -1} />
        ),
        visible: true,
      },
      {
        title: 'Configure',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'change_datastore_settings',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('change_datastore_settings') > -1} />
        ),
        visible: true,
      },
      {
        title: 'Connection',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'change_datastore_connection',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('change_datastore_connection') > -1} />
        ),
        visible: true,
      },
      {
        title: 'Metadata',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'change_datastore_metadata',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('change_datastore_metadata') > -1} />
        ),
        visible: true,
      },
      {
        title: 'Checks',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'change_datastore_checks',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('change_datastore_checks') > -1} />
        ),
        visible: datastore.supportedFeatures.checks,
      },
      {
        title: 'Comment',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'comment_on_datastore',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('comment_on_datastore') > -1} />
        ),
        visible: true,
      },
      {
        title: 'Access',
        dataIndex: 'privileges',
        align: 'center',
        editable: true,
        permission: 'change_datastore_access',
        render: (privileges) => (
          <BooleanIndicator value={privileges.indexOf('change_datastore_access') > -1} />
        ),
        visible: true,
      },
    ];

    if (this.props.hasPermission) {
      columns.push({
        align: "right",
        render: (record) => (
          <Fragment>
            {this.state.editingKey !== record.id ? (
              <>
                {/* eslint-disable-next-line*/}
                <a
                  role="button"
                  onClick={() => this.setEditingKey(record.id)}
                  className="mr-10"
                >
                  Edit
                </a>
                <RevokeDatastoreAccess datastore={this.props.datastore} contentObject={record} />
              </>
            ) : (
              <>
                {/* eslint-disable-next-line*/}
                <Button size="small" type="primary" onClick={() => this.handleSubmit(record)} disabled={this.props.submitting}>
                  {this.props.submitting ? 'Saving...' : 'Save'}
                </Button>
                <Button size="small" className="ml-5" onClick={() => this.setEditingKey('')} disabled={this.props.submitting}>
                  Cancel
                </Button>
              </>
            )}
          </Fragment>
        ),
        visible: true,
      })
    }

    return columns.filter((c) => c.visible)
  }

  handleSubmit = (record) => {
    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        datastore: { id },
      } = this.props

      const {
        editingKey: objectId,
      } = this.state

      const privileges = []

      for (let key in variables.privileges) {
        if (variables.privileges[key] === true) {
          privileges.push(key)
        }
      }

      const payload = {
        variables: { id, objectId, privileges },
        successMessage: "Changes have been saved.",
        refetchQueries: [
          {
            query: GetDatastoreAccessPrivileges,
            variables: {
              datastoreId: id,
            },
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const { ok, errors } = data.updateDatastoreAccessPrivileges

    if (!errors && ok) {
      this.setEditingKey('')
    }
  }

  setEditingKey = (editingKey) => {
    this.props.form.resetFields()
    this.setState({ editingKey })
  }

  render() {
    const {
      dataSource,
      form,
      dataTest,
    } = this.props

    const mergedColumns = this.getColumns().map(col => {
      if (!col.editable) {
        return col;
      }

      return {
        ...col,
        onCell: record => ({
          record,
          dataIndex: col.dataIndex,
          editing: record.id === this.state.editingKey,
          form: form,
          name: col.permission,
          title: col.title,
        }),
      };
    });

    return (
      <div className="datastore-access-privileges-table" data-test={dataTest}>
        <Table
          rowKey="id"
          components={{
            body: {
              cell: EditableCell,
            },
          }}
          rowClassName="editable-row"
          dataSource={dataSource}
          columns={mergedColumns}
          pagination={{ simple: true }}
          locale={{ emptyText: "Nothing here." }}
        />
      </div>
    )
  }
}

const withForm = Form.create()

export default compose(
  withForm,
  graphql(UpdateDatastoreAccessPrivilegesMutation),
  withGraphQLMutation,
)(DatastoreAccessPrivilegesTable)
