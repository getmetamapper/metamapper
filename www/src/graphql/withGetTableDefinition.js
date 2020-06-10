import { graphql } from "react-apollo"
import GetTableDefinition from "graphql/queries/GetTableDefinition"

const withGetTableDefinition = graphql(GetTableDefinition, {
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
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      tableDefinition: data.tableDefinition,
    }
  },
})

export default withGetTableDefinition
