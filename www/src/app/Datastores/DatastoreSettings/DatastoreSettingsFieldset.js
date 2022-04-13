import React from "react"
import { Card, Col, Form, Input, Row, Switch } from "antd"
import { arrayOfEmailsValidator } from "lib/validators"
import FormLabel from "app/Common/FormLabel"
import TagsInput from "app/Common/TagsInput"

const DatastoreSettingsFieldset = ({
  datastore,
  form: { getFieldDecorator },
  hasPermission,
}) => (
  <>
    <Form.Item>
      <FormLabel label="Nickname" required />
      {getFieldDecorator("name", {
        initialValue: datastore.name,
        rules: [
          { required: true, message: "Please enter an alphanumeric nickname." },
        ],
      })(
        <Input
          type="text"
          disabled={!hasPermission}
          data-test="DatastoreSettingsFieldset.Nickname"
        />
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel label="Tags" />
      {getFieldDecorator("tags", {
        initialValue: datastore.tags,
        rules: [],
      })(
        <TagsInput
          className="full-width"
          disabled={!hasPermission}
          data-test="DatastoreSettingsFieldset.Tags"
        />
      )}
    </Form.Item>
    <Form.Item>
      <FormLabel
        label="Incident Contacts"
        helpText="We will notify these people when an issue occurs, such as your datastore is not syncing properly."
      />
      {getFieldDecorator("incidentContacts", {
        initialValue: datastore.incidentContacts,
        rules: [
          { validator: arrayOfEmailsValidator },
        ],
      })(
        <TagsInput
          className="full-width"
          disabled={!hasPermission}
          data-test="DatastoreSettingsFieldset.IncidentContacts"
        />
      )}
    </Form.Item>
    {datastore && datastore.hasOwnProperty("isEnabled") && (
      <Form.Item>
        <Card className="datastore-crawling-enabled">
          <Row>
            <Col span={18}>
              <span className="label">Enable Syncing</span>
              <small>
                No definitions will be updated when syncing is disabled.
              </small>
            </Col>
            <Col span={6}>
              <span className="pull-right">
                {getFieldDecorator("isEnabled", {
                  initialValue: datastore.isEnabled,
                  rules: [],
                })(
                  <Switch
                    defaultChecked={datastore.isEnabled}
                    disabled={!hasPermission}
                    data-test="DatastoreSettingsFieldset.Enabled"
                  />
                )}
              </span>
            </Col>
          </Row>
        </Card>
      </Form.Item>
    )}
  </>
)

DatastoreSettingsFieldset.defaultProps = {
  datastore: {},
}

export default DatastoreSettingsFieldset
