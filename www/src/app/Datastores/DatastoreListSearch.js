import React from "react"
import { Form, Icon, Input } from "antd"

const DatastoreListSearch = ({
  form: { getFieldDecorator },
  search,
  onSearch,
}) => (
  <div className="datastore-search">
    <Form onSubmit={onSearch} data-test="DatastoreListSearch">
      <Form.Item label={false}>
        {getFieldDecorator("search", {
          initialValue: search,
        })(
          <Input
            suffix={<Icon type="search" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="text"
            placeholder="Search datastores..."
            data-test="DatastoreListSearch.Submit"
          />
        )}
      </Form.Item>
    </Form>
  </div>
)

export default DatastoreListSearch
