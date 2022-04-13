import React, { Fragment } from "react"
import { Col, Checkbox, Row } from "antd"

const DatastorePrivilegeCheckboxGroup = ({ form, rules, dataTest }) => (
  <Fragment>
    {form.getFieldDecorator(
      "privileges",
      {
        rules: rules,
      }
    )(
      <Checkbox.Group data-test={dataTest}>
        <Row>
          <Col>
            <Checkbox value="view_datastore">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">View Datastore</span>
                <p className="datastore-permission-desc">
                  Read-only permission for this datastore. This means the user can see almost every aspect of this datastore.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="change_datastore_settings">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Change Datastore Settings</span>
                <p className="datastore-permission-desc">
                  Can edit datastore settings, such as the nickname or tags associated with the datastore.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="change_datastore_connection">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Change Datastore Connection</span>
                <p className="datastore-permission-desc">
                  Can change the connection settings of the datastore.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="change_datastore_metadata">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Change Datastore Metadata</span>
                <p className="datastore-permission-desc">
                  Can change various metadata of the datastore and its objects, such as table descriptions and custom properties.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="change_datastore_checks">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Manage Checks</span>
                <p className="datastore-permission-desc">
                  Can manage data quality checkas associated with the datastore.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="comment_on_datastore">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Comment on Datastore</span>
                <p className="datastore-permission-desc">
                  Can comment on the datastore and its objects. This also includes pinning and removing comments.
                </p>
              </div>
            </Checkbox>
          </Col>
          <Col>
            <Checkbox value="change_datastore_access">
              <div className="checkbox-content">
                <span className="datastore-permission-lvl">Change Datastore Access</span>
                <p className="datastore-permission-desc">
                  Can update datastore access privileges, which are configurable from this page.
                </p>
              </div>
            </Checkbox>
          </Col>
        </Row>
      </Checkbox.Group>,
    )}
  </Fragment>
)

DatastorePrivilegeCheckboxGroup.defaultProps = {
  rules: [],
}

export default DatastorePrivilegeCheckboxGroup
