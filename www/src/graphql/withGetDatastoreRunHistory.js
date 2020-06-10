import { graphql } from "react-apollo"
import { map } from "lodash"
import GetDatastoreRunHistory from "graphql/queries/GetDatastoreRunHistory"

const withGetDatastoreRunHistory = graphql(GetDatastoreRunHistory, {
  skip: ({ datastore }) => !datastore.hasOwnProperty("id"),
  options: ({ datastore: { id: datastoreId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { datastoreId },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      runHistory: [],
    }

    if (data.error) {
      data.stopPolling()
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    return {
      runHistory: map(data.runHistory.edges, ({ node }) => node),
    }
  },
})

export default withGetDatastoreRunHistory
