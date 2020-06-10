import { graphql } from "react-apollo"
import { map } from "lodash"
import GetRecentDatastoreActivities from "graphql/queries/GetRecentDatastoreActivities"

const withGetRecentDatastoreActivities = graphql(GetRecentDatastoreActivities, {
  skip: ({ datastore }) => !datastore.hasOwnProperty("id"),
  options: ({ datastore: { id: datastoreId } }) => ({
    fetchPolicy: "network-only",
    pollInterval: 500,
    variables: { datastoreId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      recentDatastoreActivities: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    data.stopPolling()

    const activities = map(
      data.recentDatastoreActivities.edges,
      ({ node }) => node
    )

    return {
      recentDatastoreActivities: activities,
    }
  },
})

export default withGetRecentDatastoreActivities
