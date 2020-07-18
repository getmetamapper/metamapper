import React from "react"
import { Collapse, Icon, Tooltip } from "antd"
import { map } from "lodash"
import Link from "app/Navigation/Link"

const TableSchemaSelector = ({
  activeKey,
  currentTable,
  datastore,
  onChange,
  schemas,
}) => (
  <div className="table-schema-selector">
    <Collapse
      defaultActiveKey={[currentTable.name]}
      activeKey={activeKey}
      onChange={onChange}
    >
      {map(schemas, ({ name: schema, tables }) => (
        <Collapse.Panel
          key={schema}
          header={
            <Tooltip title={schema} placement="left">
              {schema}
            </Tooltip>
          }
        >
          {map(tables, (table, idx) => (
            <Link
              className={`tablename ${
                currentTable.name === table.name ? "active" : ""
              }`}
              key={idx}
              title={table.name}
              to={`/datastores/${datastore.slug}/definition/${schema}/${table.name}/overview`}
            >
              <Icon type="table" /> {table.name}
            </Link>
          ))}
        </Collapse.Panel>
      ))}
    </Collapse>
  </div>
)

export default TableSchemaSelector
