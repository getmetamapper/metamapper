import React from "react"
import GenericConnectionFieldset from "./GenericConnectionFieldset"
import SnowflakeConnectionFieldset from "./SnowflakeConnectionFieldset"

const engineFieldsetMapping = {
  mysql: GenericConnectionFieldset,
  oracle: GenericConnectionFieldset,
  postgresql: GenericConnectionFieldset,
  redshift: GenericConnectionFieldset,
  snowflake: SnowflakeConnectionFieldset,
  sqlserver: GenericConnectionFieldset,
}

const ConnectionSettingsFieldset = ({ engine, ...restProps }) => {
  let Fieldset = GenericConnectionFieldset

  if (engine && engineFieldsetMapping.hasOwnProperty(engine)) {
    Fieldset = engineFieldsetMapping[engine]
  }
  return <Fieldset {...restProps} />
}

export default ConnectionSettingsFieldset
