import React from "react"
import { Form, Icon, Input } from "antd"

const DatastoreAssetSearch = ({
  form: { getFieldDecorator },
  search,
  onSearch,
}) => (
  <div className="datastore-asset-search">
    <Form onSubmit={onSearch} data-test="DatastoreAssetSearch">
      <Form.Item label={false}>
        {getFieldDecorator("search", {
          initialValue: search,
        })(
          <Input
            suffix={<Icon type="search" style={{ color: "rgba(0,0,0,.25)" }} />}
            type="text"
            placeholder="Filter assets by name..."
            data-test="DatastoreAssetSearch.Submit"
          />
        )}
      </Form.Item>
    </Form>
  </div>
)

export default DatastoreAssetSearch
