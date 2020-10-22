import { graphql } from "react-apollo"
import GetTableLastCommitTimestamp from "graphql/queries/GetTableLastCommitTimestamp"

const withGetTableDefinition = graphql(GetTableLastCommitTimestamp, {
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
      lastCommitTimestamp: null,
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      lastCommitTimestamp: data.tableLastCommitTimestamp,
    }
  },
})

export default withGetTableDefinition
