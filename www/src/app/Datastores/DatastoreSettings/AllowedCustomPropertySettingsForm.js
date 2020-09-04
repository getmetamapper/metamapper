import React from "react"
import { Alert, Form } from "antd"
import Link from "app/Navigation/Link"
import RestrictedButton from "app/Common/RestrictedButton"
import AllowedCustomPropertySettingsFieldset from "./AllowedCustomPropertySettingsFieldset"

const CustomFieldLink = (props) => <Link to="/settings/customproperties">custom properties </Link>

const AllowedCustomPropertySettingsForm = ({
  form,
  datastore,
  customDatastoreFields,
  enabledDatastoreProperties,
  customTableFields,
  enabledTableProperties,
  hasPermission,
  isSubmitting,
  onSubmit,
}) => (
  <Form onSubmit={onSubmit} className="custom-property-settings-form">
    <Alert message={
      <span>
        Metamapper allows you to add globally-defined <CustomFieldLink />
        to certain datastore objects. Use this section to disable
        a property specifically for the <b>{datastore.name}</b> datastore.
      </span>
    }/>
    <AllowedCustomPropertySettingsFieldset
      form={form}
      customDatastoreFields={customDatastoreFields}
      enabledDatastoreProperties={enabledDatastoreProperties}
      customTableFields={customTableFields}
      enabledTableProperties={enabledTableProperties}
      hasPermission={hasPermission}
    />
    {/* We disable the form button if no custom fields exist */}
    <Form.Item>
      <RestrictedButton
        type="primary"
        htmlType="submit"
        hasPermission={hasPermission}
        disabled={customDatastoreFields.length === 0 && customTableFields.length === 0}
        isSubmitting={isSubmitting}
        data-test="AllowedCustomPropertySettingsForm.Submit"
      >
        {isSubmitting ? "Saving..." : "Save Changes"}
      </RestrictedButton>
    </Form.Item>
  </Form>
)

export default AllowedCustomPropertySettingsForm
