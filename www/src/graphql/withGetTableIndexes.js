import { graphql } from "react-apollo"
import { map, orderBy } from "lodash"
import GetTableIndexes from "graphql/queries/GetTableIndexes"

const withGetTableIndexes = graphql(GetTableIndexes, {
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
      tableIndexes: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { tableDefinition } = data

    if (!tableDefinition) {
      return res
    }

    const { indexes } = tableDefinition

    if (!indexes || !indexes.hasOwnProperty("edges")) {
      return res
    }

    data.stopPolling()

    return {
      tableDefinition,
      tableIndexes: orderBy(
        map(indexes.edges, ({ node }) => node),
        "createdAt"
      ),
    }
  },
})

export default withGetTableIndexes
