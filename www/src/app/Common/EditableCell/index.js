import React, { Component } from "react"
import { Icon, Input, Form } from "antd"

const EditableContext = React.createContext()

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
)

export const EditableFormRow = Form.create()(EditableRow)

export class EditableCell extends Component {
  state = {
    editing: false,
  }

  toggleEdit = () => {
    const editing = !this.state.editing
    this.setState({ editing }, () => {
      if (editing) {
        this.input.focus()
      }
    })
  }

  save = (e) => {
    const { record, handleSave } = this.props
    this.form.validateFields((error, values) => {
      if (error && error[e.currentTarget.id]) {
        return
      }
      this.toggleEdit()
      handleSave({ ...record, ...values })
    })
  }

  renderCell = (form) => {
    this.form = form
    const { children, dataIndex, record, rules, icon } = this.props
    const { editing } = this.state
    return editing ? (
      <Form.Item style={{ margin: 0 }}>
        {form.getFieldDecorator(dataIndex, {
          rules,
          initialValue: record[dataIndex],
        })(
          <Input.TextArea
            ref={(node) => (this.input = node)}
            onPressEnter={this.save}
            onBlur={this.save}
            data-test="EditableCell.Input"
            rows={3}
          />
        )}
      </Form.Item>
    ) : (
      <div className="editable-cell-value-wrap" onClick={this.toggleEdit}>
        {icon && (
          <span className="editable-cell-icon">
            <Icon type={icon} />
          </span>
        )}
        <>{children}</>
      </div>
    )
  }

  render() {
    const {
      editable,
      dataIndex,
      record,
      index,
      handleSave,
      children,
      ...restProps
    } = this.props
    return (
      <td {...restProps}>
        {editable ? (
          <EditableContext.Consumer>{this.renderCell}</EditableContext.Consumer>
        ) : (
          children
        )}
      </td>
    )
  }
}

EditableCell.defaultProps = {
  icon: "edit",
  rules: [],
}

export const components = {
  body: {
    row: EditableFormRow,
    cell: EditableCell,
  },
}
