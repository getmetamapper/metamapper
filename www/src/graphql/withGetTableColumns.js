import { graphql } from "react-apollo"
import { map, orderBy } from "lodash"
import GetTableColumns from "graphql/queries/GetTableColumns"

const withGetTableColumns = graphql(GetTableColumns, {
  skip: ({ datastore }) => !datastore.hasOwnProperty("id"),
  options: ({
    datastore: { id: datastoreId },
    match: {
      params: { schemaName, tableName },
    },
  }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: {
      datastoreId,
      schemaName,
      tableName,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      tableDefinition: {},
      tableColumns: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    const { tableDefinition } = data
    const { columns } = tableDefinition

    return {
      tableDefinition,
      tableColumns: orderBy(
        map(columns.edges, ({ node }) => node),
        "ordinalPosition"
      ),
    }
  },
})

export default withGetTableColumns
