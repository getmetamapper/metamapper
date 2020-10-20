import { graphql } from "react-apollo"
import GetColumnDefinition from "graphql/queries/GetColumnDefinition"

const withGetColumnDefinition = graphql(GetColumnDefinition, {
  skip: ({ datastore }) => !datastore.hasOwnProperty("id"),
  options: ({
    datastore: { id: datastoreId },
    match: {
      params: { schemaName, tableName, columnName },
    },
  }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: {
      datastoreId,
      schemaName,
      tableName,
      columnName,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      columnDefinition: {},
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      columnDefinition: data.columnDefinition,
    }
  },
})

export default withGetColumnDefinition
