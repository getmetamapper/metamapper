import { graphql } from "react-apollo"
import { map } from "lodash"
import GetRecentUserActivities from "graphql/queries/GetRecentUserActivities"

const withGetRecentUserActivities = graphql(GetRecentUserActivities, {
  options: ({
    match: {
      params: { userId },
    },
  }) => ({
    fetchPolicy: "network-only",
    variables: { userId },
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      recentUserActivities: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const {
      recentUserActivities: activities
    } = data

    if (!activities || !activities.hasOwnProperty("edges")) {
      return res
    }

    return {
      recentUserActivities: map(activities.edges, ({ node }) => node),
    }
  },
})

export default withGetRecentUserActivities
