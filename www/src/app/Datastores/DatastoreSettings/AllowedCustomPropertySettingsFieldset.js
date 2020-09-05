import React from "react"
import { Form, Tooltip, Checkbox } from "antd"
import { map } from "lodash"
import FormLabel from "app/Common/FormLabel"


const AllowedCustomPropertySettingsFieldset = ({
  form: { getFieldDecorator },
  customDatastoreFields,
  enabledDatastoreProperties,
  customTableFields,
  enabledTableProperties,
  hasPermission,
}) => (
  <div className="custom-property-settings-fieldset">
    <Form.Item>
      <FormLabel label="Datastore Properties" />
      <small>
        {customDatastoreFields.length > 0 ? (
          <span>Check the box next to the property name to enable.</span>
        ) : (
          <span>No datastore custom properties exist in this workspace.</span>
        )}
      </small>
      {getFieldDecorator("enabledDatastoreProperties", {
        initialValue: enabledDatastoreProperties,
        rules: [],
      })(
        <Checkbox.Group>
          {map(customDatastoreFields, ({ pk, fieldName, shortDesc }) => (
            <span className="ant-checkbox-group-item">
              <Tooltip title={shortDesc} placement="right">
                <Checkbox value={pk} /> {fieldName}
              </Tooltip>
            </span>
          ))}
        </Checkbox.Group>
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Table Properties" />
      <small>
        {customTableFields.length > 0 ? (
          <span>Check the box next to the property name to enable.</span>
        ) : (
          <span>No table custom properties exist in this workspace.</span>
        )}
      </small>
      {getFieldDecorator("enabledTableProperties", {
        initialValue: enabledTableProperties,
        rules: [],
      })(
        <Checkbox.Group>
          {map(customTableFields, ({ pk, fieldName, shortDesc }) => (
            <span className="ant-checkbox-group-item">
              <Tooltip title={shortDesc} placement="right">
                <Checkbox value={pk} /> {fieldName}
              </Tooltip>
            </span>
          ))}
        </Checkbox.Group>
      )}
    </Form.Item>
  </div>
)

AllowedCustomPropertySettingsFieldset.defaultProps = {
  datastore: {},
}

export default AllowedCustomPropertySettingsFieldset
