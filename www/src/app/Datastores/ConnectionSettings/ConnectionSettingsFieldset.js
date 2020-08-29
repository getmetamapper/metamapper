import React from "react"
import GenericConnectionFieldset from "./GenericConnectionFieldset"
import SnowflakeConnectionFieldset from "./SnowflakeConnectionFieldset"
import AwsAthenaConnectionFieldset from "./AwsAthenaConnectionFieldset"
import AwsGlueConnectionFieldset from "./AwsGlueConnectionFieldset"
import BigQueryConnectionFieldset from "./BigQueryConnectionFieldset"
import HiveMetastoreConnectionFieldset from "./HiveMetastoreConnectionFieldset"

const engineFieldsetMapping = {
  athena: AwsAthenaConnectionFieldset,
  azure_dwh: GenericConnectionFieldset,
  azure_sql: GenericConnectionFieldset,
  bigquery: BigQueryConnectionFieldset,
  glue: AwsGlueConnectionFieldset,
  hive: HiveMetastoreConnectionFieldset,
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
