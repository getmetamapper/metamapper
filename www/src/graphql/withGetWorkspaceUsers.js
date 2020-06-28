import { graphql } from "react-apollo"
import { map } from "lodash"
import GetWorkspaceUsers from "./queries/GetWorkspaceUsers"

const withGetWorkspaceUsers = graphql(GetWorkspaceUsers, {
  options: ({ currentWorkspace: { id: workspaceId } }) => ({
    fetchPolicy: "network-only",
    variables: {
      workspaceId,
      activeOnly: false,
    },
  }),
  props: ({ data, ownProps }) => {
    const res = {
      loading: data && data.loading,
      errored: data && data.error,
      refetch: data && data.refetch,
      workspaceUsers: [],
    }

    if (!data || data.loading || data.error) {
      return res
    }

    const { workspaceUsers } = data

    if (!workspaceUsers || !workspaceUsers.hasOwnProperty("edges")) {
      return res
    }

    return {
      workspaceUsers: map(workspaceUsers.edges, ({ node }) => node),
    }
  },
})

export default withGetWorkspaceUsers
