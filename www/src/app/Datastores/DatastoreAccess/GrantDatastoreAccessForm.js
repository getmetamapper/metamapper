import React from "react"
import { Button, Form, Select } from "antd"
import { map } from "lodash"
import DatastorePrivilegeCheckboxGroup from "./DatastorePrivilegeCheckboxGroup"

const GrantDatastoreAccessForm = ({
  form,
  hasPermission,
  objectLabel,
  objectLookup,
  objects,
  testLabel,
  onSubmit,
  isSubmitting,
}) => (
  <Form onSubmit={onSubmit} className="grant-datastore-access-form" data-test={testLabel}>
    <Form.Item label={objectLabel}>
      {form.getFieldDecorator(
        "objectId",
        {
          rules: [
            { required: true, message: 'This field is required.' }
          ]
        }
      )(
        <Select
          showSearch
          data-test={`${testLabel}.ObjectId`}
          filterOption={(input, option) =>
            option.props.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
          }
         >
          {map(objects, (object) => (
            <Select.Option value={object[objectLookup]}>
              {object.name}
            </Select.Option>
          ))}
        </Select>
      )}
    </Form.Item>
    <Form.Item
      label={
        <span>
          <span>Assign Access Privileges</span>
          <small className="reset-privileges" onClick={() => form.setFieldsValue({ privileges: [] })}>(click to reset)</small>
        </span>
      }
    >
      <DatastorePrivilegeCheckboxGroup
        form={form}
        rules={[
          { required: true, message: 'Please select at least one privilege.'},
        ]}
        dataTest={`${testLabel}.Privileges`}
      />
    </Form.Item>
    <Form.Item>
      <Button
        block
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test={`${testLabel}.Submit`}
      >
        {isSubmitting ? "Creating..." : "Grant Access"}
      </Button>
    </Form.Item>
  </Form>
)

GrantDatastoreAccessForm.defaultProps = {
  objectLookup: "id",
}

export default GrantDatastoreAccessForm
