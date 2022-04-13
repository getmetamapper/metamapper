import React from "react"
import CheckSetupHandlerFieldset from "./CheckSetupHandlerFieldset"

const CheckSetupExpectationFieldset = ({ form, queryColumns, handler }) => (
  <CheckSetupHandlerFieldset
    form={form}
    field="handlerInput"
    queryColumns={queryColumns}
    handler={handler}
  />
)

export default CheckSetupExpectationFieldset
