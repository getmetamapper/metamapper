import React from "react"
import { map } from "lodash"
import KeyValuePill from "app/Common/KeyValuePill"

const TablePropertiesPillGroup = ({ properties }) => (
  <>
    {typeof properties === "object" && Object.keys(properties).length > 0 && (
      <div className="table-properties">
        {map(Object.keys(properties), (key) => (
          <KeyValuePill keyname={key} value={properties[key]} key={key} />
        ))}
      </div>
    )}
  </>
)

TablePropertiesPillGroup.defaultProps = {
  properties: {},
}

export default TablePropertiesPillGroup
