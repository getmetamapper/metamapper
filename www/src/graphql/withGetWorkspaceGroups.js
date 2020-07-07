import { graphql } from "react-apollo"
import { map } from "lodash"
import GetWorkspaceGroups from "./queries/GetWorkspaceGroups"

const withGetWorkspaceGroups = graphql(GetWorkspaceGroups, {
  options: () => ({
    fetchPolicy: "network-only",
  }),
  props: ({ data }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspaceGroups: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { workspaceGroups } = data

    if (!workspaceGroups || !workspaceGroups.hasOwnProperty("edges")) {
      return res
    }

    return {
      workspaceGroups: map(workspaceGroups.edges, ({ node }) => node),
    }
  },
})

export default withGetWorkspaceGroups
